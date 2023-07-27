# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command, fields, models, _
import requests
import logging
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    has_insurance = fields.Selection(related="category_id.has_insurance")
    insurance_request_id = fields.Many2one('insurance.request', string='Student Insurance')

    approval_message = fields.Many2one('in.messaging', string='Approval Message', domain=[('type', '=', 'approved')],
                                       store=True)
    refusal_message = fields.Many2one('in.messaging', string='Refusal Message', domain=[('type', '=', 'rejected')],
                                      store=True)

    def action_approve_with_message(self, approver=None):
        if self.approval_type == 'insurance' and self.insurance_request_id.id:
            self.insurance_request_id.write({'state': 'approved'})
            phone = "".join([c for c in self.insurance_request_id.student_phone if c.isdigit()])
            messaging_api = self.env['in.messaging.api'].search([('active_account', '=', True)], limit=1)
            if not messaging_api.id:
                raise UserError(_("There is no active messaging api account"))
            username = messaging_api.username
            password = messaging_api.password
            sender = messaging_api.sender
            response = requests.get(url=f"https://bms.syriatel.sy/API/SendSMS.aspx?user_name={username}&password="
                                        f"{password}&msg={self.approval_message.name}&sender={sender}&to="
                                        f"{phone}", verify=False)
            if response:
                if not response.text.isdigit():
                    raise ValidationError(_("An error happened when sending the message!\nEither there is a connection error or the request owner number is incorrect."))
        return super().action_approve(approver)

    def action_refuse_with_message(self, approver=None):
        if self.approval_type == 'insurance' and self.insurance_request_id.id:
            self.insurance_request_id.write({'state': 'refused'})
            phone = "".join([c for c in self.insurance_request_id.student_phone if c.isdigit()])
            messaging_api = self.env['in.messaging.api'].search([('active_account', '=', True)], limit=1)
            if not messaging_api.id:
                raise UserError(_("You don't have an active messaging api account"))
            username = messaging_api.username
            password = messaging_api.password
            sender = messaging_api.sender
            response = requests.get(url=f"https://bms.syriatel.sy/API/SendSMS.aspx?user_name={username}&password="
                                        f"{password}&msg={self.refusal_message.name}&sender={sender}&to="
                                        f"{phone}", verify=False)
            if response:
                if not response.text.isdigit():
                    raise ValidationError(_("An error happened when sending the message!\nEither there is a connection error or the request owner number is incorrect."))
        return super().action_approve(approver)

    def action_approve(self, approver=None):
        if self.approval_type == 'insurance' and self.insurance_request_id.id:
            self.insurance_request_id.write({'state': 'approved'})
        return super().action_approve(approver)

    def action_refuse(self, approver=None):
        if self.approval_type == 'insurance' and self.insurance_request_id.id:
            self.insurance_request_id.write({'state': 'refused'})
        return super().action_approve(approver)

    def action_confirm(self):
        if self.approval_type == 'insurance' and self.insurance_request_id.id:
            self.insurance_request_id.write({'state': 'waiting'})
        return super().action_confirm()

    def action_withdraw(self, approver=None):
        if self.approval_type == 'insurance' and self.insurance_request_id.id:
            self.insurance_request_id.write({'state': 'waiting'})
        return super().action_withdraw(approver)

    def action_draft(self):
        if self.approval_type == 'insurance' and self.insurance_request_id.id:
            self.insurance_request_id.write({'state': 'waiting'})
        return super().action_draft()

    def action_cancel(self):
        if self.approval_type == 'insurance' and self.insurance_request_id.id:
            self.insurance_request_id.unlink()
        return super().action_cancel()
