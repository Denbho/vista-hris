# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class EmployeeValidity(models.Model):
    _name = 'hr_coe.date_validity'
    _description = 'Display Validity'
    _rec_name = 'emp_certificate_id'

    emp_certificate_id = fields.Many2one(comodel_name="employee.certificate", readonly=True)
    employee_id = fields.Many2one(comodel_name="hr.contract", related='emp_certificate_id.employee_id')
    date_start = fields.Date(related="emp_certificate_id.date_start" ,default=datetime.today(), string="Date Start")
    date_valid = fields.Date('Date Valid', required=True)
    # user_signature = fields.Binary(string=" Draw your Signature")

    @api.model
    def create(self, vals_lists):
        return super(EmployeeValidity, self).create(vals_lists);


