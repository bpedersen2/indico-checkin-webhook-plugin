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

from flask import flash, redirect

from indico.modules.events.management.controllers import RHManageEventBase
from indico.web.forms.base import FormDefaults
from indico.web.flask.util import url_for

from indico_checkin_webhook import _
from indico_checkin_webhook.forms import EventSettingsForm
from indico_checkin_webhook import checkin_webhook_event_settings
from indico_checkin_webhook.views import WPCheckinWebhookEventMgmt


class RHCheckinWebhookManageEvent(RHManageEventBase):
    EVENT_FEATURE = 'checkin_webhook'

    def _process(self):
        form = EventSettingsForm(prefix='checkin_webhook-',
                                 event=self.event,
                                 obj=FormDefaults(**checkin_webhook_event_settings.get_all(self.event)))
        if form.validate_on_submit():

            checkin_webhook_event_settings.set_multi(self.event, form.data)
            flash(_('Settings saved'), 'success')
            return redirect(url_for('.configure', self.event))
        return WPCheckinWebhookEventMgmt.render_template('checkinwebhookmanage.html', self.event, form=form)
