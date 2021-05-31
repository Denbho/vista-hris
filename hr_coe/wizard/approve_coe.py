# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ApproveCOE(models.TransientModel):
    _name = 'hr.employee.approve.coe'
    _description = 'Create Date Validity'

    date_validity = fields.Date(string="Date Validity")
    user_sign = fields.Binary(string=" Draw your Signature")

    def action_confirm(self):
        coe = self.env['employee.certificate'].browse(self._context.get('active_id'))
        coe.write({
            'date_valid': self.date_validity,
            'user_signature': self.user_sign,
        })
        coe.approve_request()
        return True
