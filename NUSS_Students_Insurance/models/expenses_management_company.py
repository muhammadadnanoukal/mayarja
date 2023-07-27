# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import base64
from werkzeug.urls import url_encode


class ExpensesManagementCompany(models.Model):
    _name = "expenses.management.company"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Expenses Management Company'

    image_256 = fields.Image(max_width=256, max_height=256, store=True, required=True)
    name = fields.Char(string='Company Name', required=True)
    quadruple_phone = fields.Char(string='Quadruple Phone', required=True)
    phone = fields.Char(string='Phone', required=True)
    mobile_phone = fields.Char(string='Mobile Phone', required=True)
    website = fields.Char(string='Website', required=True)
    medical_network_file = fields.Binary(string='Medical Network File')
    medical_network_filename = fields.Char()
    university_ids = fields.One2many('in.university', 'emc_id', string='Universities', domain="[('type', '=', 'university')]")

