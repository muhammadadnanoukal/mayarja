# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InsuranceType(models.Model):
    _name = 'insurance.type'
    _description = 'Insurance Types'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    coverages = fields.Html(string='Coverages', required=True)
    financial_limit = fields.Char(string='Financial Limit', store=True, required=True)
    insurance_fees = fields.Integer(string='Insurance Fees', store=True, required=True)
    insurance_type = fields.Selection([('type_1', 'حوادث شخصية'),
                                       ('type_2', 'أنواع أخرى')],
                                      required=True, default='type_2', store=True)
