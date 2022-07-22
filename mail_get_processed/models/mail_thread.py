# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import email
try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

from odoo import _, api, exceptions, fields, models, tools, registry, SUPERUSER_ID

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_process(self, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None):
        # extract message bytes - we are forced to pass the message as binary because
        # we don't know its encoding until we parse its headers and hence can't
        # convert it to utf-8 for transport between the mailgate script and here.
        if isinstance(message, xmlrpclib.Binary):
            message = bytes(message.data)
        if isinstance(message, str):
            message = message.encode('utf-8')
        message = email.message_from_bytes(message)

        # parse the message, verify we are not in a loop by checking message_id is not duplicated
        msg_dict = self.message_parse(message, save_original=save_original)
        if strip_attachments:
            msg_dict.pop('attachments', None)

        # find possible routes for the message
        routes = self.message_route(message, msg_dict, model, thread_id, custom_values)
        thread_id = self._message_route_process(message, msg_dict, routes)
        return thread_id
