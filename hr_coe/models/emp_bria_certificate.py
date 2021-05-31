# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class EmployeeCerfificate(models.Model):
    _name = 'employee.certificate'
    _description = 'Employee Certificate Template'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin', 'document.default.approval']

    name = fields.Char('Request Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True, readonly=True,
                                  states={'draft': [('readonly', False)]}, track_visibility="always")
    certificate_type = fields.Selection([('COE', 'COE'), ('COEC', 'COEC')], string="Type", defualt='COE',
                                        readonly=True, states={'draft': [('readonly', False)]},
                                        track_visibility="always")
    job_id = fields.Many2one('hr.job', string="Job Position")
    department_id = fields.Many2one('hr.department', string="Department")
    date_start = fields.Date(string='Date Start')
    purpose = fields.Many2one('employee.purpose', string='Purpose', readonly=True,
                              states={'draft': [('readonly', False)]}, track_visibility="always")
    date_valid = fields.Date(string="Date Valid", readonly=True, track_visibility="always")
    user_signature = fields.Binary(string="Draw your Signature")
    old_name = fields.Char(related='company_id.old_name', string="Old name", readonly=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    downloaded = fields.Boolean(string="Downloaded")

    @api.onchange('employee_id')
    def _get_onchange_employee_id(self):
        if self.employee_id:
            self.job_id = self.employee_id.contract_id.job_id.id
            self.department_id = self.employee_id.contract_id.department_id.id
            contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)], order='date_start asc')
            if contracts[:1]:
                self.date_start = contracts[0].date_start

    def print_report(self):
        self.downloaded = True
        return self.env.ref('hr_coe.action_emp_certificate_pdf').report_action(self)

    def submit_request(self):
        self.write({'name': self.env['ir.sequence'].get('personnel.requisition')})
        super(EmployeeCerfificate, self).submit_request()


class EmployeePurpose(models.Model):
    _name = 'employee.purpose'

    name = fields.Char(string="Purpose")
