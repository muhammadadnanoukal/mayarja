# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import string
import random
import datetime

class InsuranceRequest(models.Model):
    _name = 'insurance.request'
    _description = 'Insurance Request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    request_owner_id = fields.Many2one('res.users', string='حساب الطالب')
    name = fields.Char(string='Name', readonly=True, required=True, default=lambda self: _('New'))
    related_to_self_count = fields.Integer(compute='_compute_related_to_self_count')
    student_phone = fields.Char(string='رقم الهاتف', required=True)
    first_name = fields.Char(string='الاسم', required=True)
    second_name = fields.Char(string='الكنية', required=True)
    insurance_type_id = fields.Many2one('insurance.type', string='نوع التأمين', required=True)
    fa_name = fields.Char(string='اسم الأب', required=True)
    mo_name = fields.Char(string='اسم الأم', required=True)
    gender = fields.Selection(
        [('male', "ذكر"),
         ('female', "أنثى")],
        string='الجنس', required=True)
    social_status = fields.Selection(
        [('single', 'أعزب'),
         ('married', 'متزوج')],
        string='الحالة الإجتماعية', required=True)
    birthday = fields.Date(string='تاريخ الميلاد', required=True)
    id_number = fields.Char(string='الرقم الوطني', required=True)
    id_card_front = fields.Binary(string='الوجه الأمامي للهوية', required=True)
    id_card_back = fields.Binary(string='الوجه الخلفي للهوية', required=True)
    university_id_number = fields.Char(string='الرقم الجامعي', required=True)
    place_of_accommodation = fields.Selection(
        [('damascus', "دمشق"),
         ('rif_dimashq', "ريف دمشق"),
         ('aleppo', "حلب"),
         ('latakia', "اللاذقية"),
         ('homs', "حمص"),
         ('tartus', "طرطوس"),
         ('hama', "حماة"),
         ('arraqqah', "الرقة"),
         ('alhasakah', "الحسكة"),
         ('assuwayda', "السويداء"),
         ('quneitra', "القنيطرة"),
         ('idlib', "إدلب"),
         ],
        string='مكان الإقامة', required=True)
    university_id = fields.Many2one('in.university', string='الجامعة', domain="[('type', '=', 'university')]", required=True)
    faculty_id = fields.Many2one('in.university', string='الكلية', domain="[('type', '=', 'collage'), ('parent_id', '=', university_id)]", required=True)
    academic_year = fields.Selection(
        [('first_year', "سنة أولى"),
         ('second_year', "سنة ثانية"),
         ('third_year', "سنة ثالثة"),
         ('fourth_year', "سنة رابعة"),
         ('fifth_year', "سنة خامسة"),
         ('sixth_year', "سنة سادسة"),
         ('diploma', "دبلوم"),
         ('master', "ماجستير"),
         ('doctorate', "دكتوراه"),
         ],
        string='السنة الدراسية', required=True)
    university_card = fields.Binary(string='البطاقة الجامعية', required=True)
    state = fields.Selection([
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('paid', 'Paid'),
        ('expired', 'Expired')],
        string='Status', index=True, readonly=True, copy=False,
        default='waiting', tracking=True)
    is_expired = fields.Boolean('Is Expired', compute='_compute_is_expired', default=False)

    @api.depends('state')
    def _compute_is_expired(self):
        for rec in self:
            if rec.insurance_expiration_date:
                if rec.insurance_expiration_date < datetime.datetime.today().date():
                    rec.is_expired = True
                    rec.state = 'expired'
                else:
                    rec.state = 'paid'
                    rec.is_expired = False
            else:
                rec.is_expired = False

    @api.onchange('insurance_expiration_date')
    def _onchange_expiration_date(self):
        self._compute_is_expired()

    payment_operation_id = fields.Many2one('in.payment.operation', string="Payment Operation", readonly=True)
    insurance_number = fields.Char('Insurance Number')
    insurance_expiration_date = fields.Date('Insurance Expiration Date')
    expenses_company_id = fields.Many2one('expenses.management.company', string='Expenses Management Company', compute='_compute_emc')
    approver_notes = fields.Text(string='Notes', store=True)

    @api.depends('university_id')
    def _compute_emc(self):
        for rec in self:
            if rec.university_id.emc_id.id:
                rec.expenses_company_id = rec.university_id.emc_id.id
            else:
                rec.expenses_company_id = False


    @api.depends('name')
    def _compute_related_to_self_count(self):
        for rec in self:
            rec.related_to_self_count = len(self.env['approval.request'].search([('insurance_request_id', '=', self.id)]))

    def show_related_approval(self):
        self.ensure_one()
        action = {
            'name': 'Related Approvals',
            'res_model': 'approval.request',
            'type': 'ir.actions.act_window',
        }
        recs = self.env['approval.request'].search([('insurance_request_id', '=', self.id)])
        if self.related_to_self_count == 1:
            action['res_id'] = recs[0].id
            action['view_mode'] = 'form'
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', recs.ids)]
        return action

    def show_payment_operation(self):
        return {
            'name': 'Payment Operation',
            'type': 'ir.actions.act_window',
            'res_model': 'in.payment.operation',
            'view_mode': 'tree',
            'domain': [('id', '=', self.payment_operation_id.id)]
        }

    def generate_random_uid(self, num_of_digit):
        random_id_number = ''.join([random.choice(string.digits) for n in range(num_of_digit)])
        return random_id_number

    @api.onchange('id_number')
    def _onchange_id_number(self):
        for rec in self:
            if rec.id_number:
                if not rec.id_number.isdigit():
                    raise ValidationError(_('الرقم الوطني خاطئ'))

    def write(self, vals):
        if 'id_number' in vals:
            if not vals['id_number'].isdigit():
                raise ValidationError(_('الرقم الوطني خاطئ'))
        return super(InsuranceRequest, self).write(vals)

    @api.model
    def create(self, vals):
        if 'id_number' in vals:
            if not vals['id_number'].isdigit():
                raise ValidationError(_('الرقم الوطني خاطئ'))
        if vals.get('name', _('New')) == _('New'):
            seq_name = self.generate_random_uid(6)
            all_requests_names = self.env['insurance.request'].search([]).mapped('name')
            while seq_name in all_requests_names:
                seq_name = self.generate_random_uid(6)
            vals['name'] = seq_name or _('New')
        res = super(InsuranceRequest, self).create(vals)

        approved_message_search_res = self.env['in.messaging'].sudo().search([('type', '=', 'approved')], order='id')
        rejected_message_search_res = self.env['in.messaging'].sudo().search([('type', '=', 'rejected')], order='id')
        self.env['approval.request'].sudo().create({
            'category_id': self.env['approval.category'].sudo().search(
                [('approval_type', '=', 'insurance')]).id,
            'insurance_request_id': res.id,
            'request_owner_id': res.request_owner_id.id,
            'approval_message': approved_message_search_res[0].id if len(approved_message_search_res) != 0 else
            self.env['in.messaging'].sudo().create({
                'name': 'لقد تم قبول طلبك بنجاح!',
                'type': 'approved'
            }).id,
            'refusal_message': rejected_message_search_res[0].id if len(rejected_message_search_res) != 0 else
            self.env['in.messaging'].sudo().create({
                'name': 'عذراً، لقد تم رفض طلبك!',
                'type': 'rejected'
            }).id})
        return res

    def unlink(self):
        for ins_req in self:
            approvals_requests = self.env['approval.request'].search([('insurance_request_id', '=', ins_req.id)])
            for rec in approvals_requests:
                rec.sudo().unlink()
            return super().unlink()
