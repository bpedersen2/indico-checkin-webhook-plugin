# This file is part of Indico.
# Copyright (C) 2017  Bjoern Pedersen
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

from indico.modules.events.settings import EventSettingsProxy
from indico.util.i18n import make_bound_gettext

from indico.core import signals
from indico.modules.events.features.base import EventFeature

_ = make_bound_gettext('checkin_webhook')

checkin_webhook_event_settings = EventSettingsProxy('checkin_webhook', {
    'webhookurl': None,
    'ticket_template_id': None,
    'ticket_template': None,
    'send_json': False,
})


@signals.event.get_feature_definitions.connect
def _get_feature_definitions(sender, **kwargs):
    return CheckinWebhookFeature


class CheckinWebhookFeature(EventFeature):
    name = 'checkin_webhook'
    friendly_name = _('Checkin Webhook')
    requires = {'registration'}
    description = _('Gives event managers the opportunity to trigger a webhook on checkin.')

    @classmethod
    def enabled(cls, event):
        for setting in (
                'webhookurl',
                'ticket_template_id',
        ):
            if checkin_webhook_event_settings.get(event, setting) is None:
                value = ''
                checkin_webhook_event_settings.set(event, setting, value)
