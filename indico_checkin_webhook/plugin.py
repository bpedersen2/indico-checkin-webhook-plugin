# This file is part of Indico.
# Copyright (C) 2017 Bjoern Pedersen.
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import requests
from flask import json, session, request
from sqlalchemy.orm import joinedload

from indico.core import signals

from indico.core.logger import Logger
from indico.core.plugins import IndicoPlugin, url_for_plugin
from indico.web.menu import SideMenuItem
#from indico.modules.events.api import SerializerBase
from indico.modules.events.features.util import is_feature_enabled
from indico.modules.events.registration.badges import RegistrantsListToBadgesPDF, RegistrantsListToBadgesPDFFoldable
from indico.modules.events.registration.util import build_registration_api_data
from indico.util.string import slugify

from indico_checkin_webhook import _, checkin_webhook_event_settings
from indico_checkin_webhook.blueprint import blueprint

logger = Logger.get('checkin_webhook')


class CheckinWebhookPlugin(IndicoPlugin):
    """Checkin Webhook Plugin

    Triggers a webhook on checkin of a participant.

    The data POSTed to the webhook are either multipart form-encoded data
    with the selected ticket template in files[file] and the registration 
    data json-encoded in form[data] or the json-encoded registration data.

    Data layout: 
	{u'amount_paid': 0,
	 u'checked_in': True,
	 u'checkin_date': u'<timestamp>',
	 u'checkin_secret': u'<uuid>',
	 u'data_by_id': {u'<field_id>': u'<value>',
                         ....
         },
	 u'data_by_name': {u'<slugified section>_<slugified field title>': u'<value>',
                         ....
                        },
	 u'event_id': <id>,
	 u'full_name': u' Bjoern Pedersen',
	 u'paid': False,
	 u'personal_data': {u'<field name>': u'<value>',
                           .... personal data fields
                          }
         u'registrant_id': u'<registrant id>',
         u'registration_date': u'<timestamp value>'}
    
    (slugified: lowercased, spaces replace by '-', see `indico.util.string.slugify`)

    """
    configurable = True

    def init(self):
        super(CheckinWebhookPlugin, self).init()
        self.connect(signals.menu.items, self.extend_event_management_menu, sender='event-management-sidemenu')

        self.connect(signals.event.registration.registration_checkin_updated, self._handle_checkin)

    def _mode(self, registration):
        if checkin_webhook_event_settings.get(registration.event, 'send_json'):
            return 'json'
        return 'pdf'

    def _wh_url(self, event):
        return checkin_webhook_event_settings.get(event, 'webhookurl')

    def _send_json(self, registration):
        try:
            data = self.build_data(registration)

            requests.post(self._wh_url(registration.event),
                          data=json.dumps(data),
                          headers={'Content-Type': 'application/json'})
        except Exception as e:
            logger.warn(_('Could not send data (%s)'), e)

    def build_registration_data(self, reg):
        data = build_registration_api_data(reg)
        data['data_by_id'] = {}
        data['data_by_name'] = {}
        for field_id, item in reg.data_by_field.iteritems():
            data['data_by_id'][field_id] = item.friendly_data
        for item in reg.data:
            fieldname = slugify(item.field_data.field.title)
            fieldparent = slugify(item.field_data.field.parent.title)
            data['data_by_name']['{}_{}'.format(fieldparent, fieldname)] = item.friendly_data
        return data

    def build_admin_data(self):
        admin_data = {
            'user': session.user.name,
            'userid': session.user.id,
        }
        return admin_data

    def build_event_data(self, reg):
        event = reg.event
        data_attrs = [
            'additional_info',
            'address',
            'contact_emails',
            'contact_phones',
            'contact_title',
            'description',
            'duration',
            'end_dt',
            'end_dt_display',
            'end_dt_local',
            'end_dt_override',
            'external_url',
            'id',
            'keywords',
            'logo_url',
            'note',
            'organizer_info',
            'own_address',
            'own_no_access_contact',
            'own_room',
            'own_room_id',
            'own_room_name',
            'own_venue',
            'own_venue_id',
            'own_venue_name',
            'series',
            'short_external_url',
            'short_url',
            'start_dt',
            'start_dt_display',
            'start_dt_local',
            'start_dt_override',
            'timezone',
            'title',
            'type',
            'tzinfo',
            'url',
            'url_shortcut',
            'venue',
            'venue_name',
        ]

        data = {attr: str(getattr(event, attr)) for attr in data_attrs}
        return data

    def build_data(self, reg):
        return dict(data=self.build_registration_data(reg),
                    event_data=self.build_event_data(reg),
                    admin_data=self.build_admin_data())

    def _send_pdf(self, registration):
        try:

            fname = 'print-' + str(registration.id) + '.pdf'
            pdf = generate_ticket(registration)
            files = {'file': (fname, pdf, 'application/pdf', {'Expires': '0'})}
            data = self.build_data(registration)
            requests.post(self._wh_url(registration.event), data={'data': json.dumps(data)}, files=files)
        except Exception as e:
            logger.warn(_('Could not print the checkin badge (%s)'), e)

    def _handle_checkin(self, registration, **kwargs):
        if is_feature_enabled(registration.event, 'checkin_webhook') and registration.checked_in:
            mode = self._mode(registration)
            if self._mode(registration) == 'json':
                self._send_json(registration)
            elif mode == 'pdf':
                self._send_pdf(registration)

    @property
    def logo_url(self):
        return url_for_plugin(self.name + '.static', filename='images/logo.png')

    def get_blueprints(self):
        return blueprint

    def extend_event_management_menu(self, sender, event, **kwargs):
        if event.can_manage(session.user):
            return SideMenuItem('CheckinWebhook',
                                _('Checkin Webhook'),
                                url_for_plugin('checkin_webhook.configure', event),
                                section='services')

    def get_event_management_url(self, event, **kwargs):
        if event.can_manage(session.user):
            return url_for_plugin('checkin_webhook.configure', event)


def generate_ticket(registration):
    """Mostly copied from indico.module.events.registration.utils, but different ticket
       template resolution
    """

    from indico.modules.designer.util import get_default_ticket_on_category
    from indico.modules.events.registration.controllers.management.tickets import DEFAULT_TICKET_PRINTING_SETTINGS
    # default is A4

    template = checkin_webhook_event_settings.get(registration.event, 'ticket_template')
    if not template:
        template = (registration.registration_form.ticket_template
                    or get_default_ticket_on_category(registration.event.category))

    signals.event.designer.print_badge_template.send(template, regform=registration.registration_form)
    pdf_class = RegistrantsListToBadgesPDFFoldable if template.backside_template else RegistrantsListToBadgesPDF
    pdf = pdf_class(template, DEFAULT_TICKET_PRINTING_SETTINGS, registration.event, [registration.id])
    return pdf.get_pdf()
