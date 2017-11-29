# indico-checkin-webhook-plugin

Indico checkin webhook plugin
=============================

This plugin plugin listens for the `registration_checkin_updated`` signal and sends data plus possibly a 
ticket/badge pdf to a listening webhook. 

The data POSTed to the webhook are either multipart form-encoded data
with the selected ticket template in files[file] and the registration 
data json-encoded in form[data] or the json-encoded registration data.
 
Data layout:
-----------

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
