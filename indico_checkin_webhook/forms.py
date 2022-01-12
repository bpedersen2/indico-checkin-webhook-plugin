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

from wtforms.fields import BooleanField, SelectField, URLField
from wtforms.validators import DataRequired

from indico.web.forms.base import IndicoForm
from indico.modules.designer import TemplateType
from indico.modules.designer.util import get_default_ticket_on_category, get_inherited_templates
from indico.web.forms.widgets import SwitchWidget

from indico_checkin_webhook import _

WEBHOOK_DESC = """Provide an URL to be called as a webhook with the badge pdf
as argument"""


class EventSettingsForm(IndicoForm):
    #event_specific_fields = ['webhookurl']
    webhookurl = URLField(_('webhook-url'), [DataRequired()], description=WEBHOOK_DESC)
    ticket_template_id = SelectField(_('Ticket template'), [DataRequired()], coerce=int)
    send_json = BooleanField(_('Send only JSON data'), widget=SwitchWidget())

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        super(EventSettingsForm, self).__init__(*args, **kwargs)
        default_tpl = get_default_ticket_on_category(event.category)
        all_templates = set(event.designer_templates) | get_inherited_templates(event)
        badge_templates = [(tpl.id, tpl.title) for tpl in all_templates
                           if tpl.type == TemplateType.badge and tpl != default_tpl]
        # Show the default template first
        badge_templates.insert(0,
                               (default_tpl.id, '{} ({})'.format(default_tpl.title, _('Default category template'))))
        self.ticket_template_id.choices = badge_templates
