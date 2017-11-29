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

from indico.core.db import db
from indico.modules.designer.models.templates import DesignerTemplate


class CheckinWebhook(db.Model):
    """Checkin Webhook settings"""
    __tablename__ = 'checkin_webhook_settings'
    __table_args__ = ({'schema': 'plugin_checkin_webhook'})

    #: Entry ID
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    #: ID of the associated registration
    event_id = db.Column(
        db.Integer,
        db.ForeignKey('events.events.id'),
        index=True,
        nullable=False
    )
    #: the webhookurl
    webhookurl = db.Column(
        db.String,
        nullable=False
    )

    ticket_template_id = db.Column(
        db.Integer,
        db.ForeignKey(DesignerTemplate.id),
        index=True,
        nullable=False
    )
    #: The template used to generate tickets
    ticket_template = db.relationship(
        'DesignerTemplate',
        lazy=True,
        foreign_keys=ticket_template_id,
        backref=db.backref(
            'ticket_for_checkin',
            lazy=True
        )
    )
    #: Send data as json
    send_json = db.Column(
        db.Boolean,
        default=False,
        nullable=False)
