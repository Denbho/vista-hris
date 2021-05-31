# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class EmpValid(models.TransientModel):
    _name = 'hr_coe.date_popup'
    _description = 'Create Date Validity'

    emp_certificate_id = fields.Many2one(comodel_name='employee.certificate', readonly=True)
    dt_validity = fields.Date(string="Date Validity")
    # user_sign = fields.Binary(string=" Draw your Signature")

    def action_confirm(self):
        validity = self.env['hr_coe.date_validity'].create({
            'emp_certificate_id': self.emp_certificate_id.id,
            'date_valid': self.dt_validity
            # 'user_signature': self.user_sign
        })  
        self.emp_certificate_id.update({
            'valid_id': validity.id,
        })
        self.emp_certificate_id.update({
            'state': 'approved' 
        })

        