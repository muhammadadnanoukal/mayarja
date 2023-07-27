# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    insurance_requests_count = fields.Integer(
        'My Insurance Requests', compute='_compute_insurance_requests')

    def _compute_insurance_requests(self):
        self.insurance_requests_count = 0
        for partner in self:
            partner.event_count = self.env['insurance.request'].search_count([('request_owner_id.partner_id', '=', partner.id)])