# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime, date


class HREmployeeMovement(models.Model):
    _inherit = "hr.employee.movement"

    curr_employment_type_id = fields.Many2one('hr.employment.type', string="Employment Type", track_visibility="always",
                                        readonly=True, states={'draft': [('readonly', False)]})
    curr_employment_status_id = fields.Many2one('hr.employment.status', string="Employment Status", track_visibility="always",
                                            readonly=True, states={'draft': [('readonly', False)]})
    curr_company_assignment_id = fields.Many2one('res.company', string="Company Assignment", track_visibility="always",
                                            readonly=True, states={'draft': [('readonly', False)]})
    employment_type_id = fields.Many2one('hr.employment.type', string="New Employment Type", track_visibility="always",
                                        readonly=True, states={'draft': [('readonly', False)]})
    employment_status_id = fields.Many2one('hr.employment.status', string="New Employment Status", track_visibility="always",
                                            readonly=True, states={'draft': [('readonly', False)]})
    company_assignment_id = fields.Many2one('res.company', string="New Company Assignment", track_visibility="always",
                                            readonly=True, states={'draft': [('readonly', False)]})

    def contract_data(self):
        res = super(HREmployeeMovement, self).contract_data()
        res['employment_type_id'] = self.employment_type_id and self.employment_type_id.id or False
        res['employment_status_id'] = self.employment_status_id and self.employment_status_id.id or False
        res['company_assignment_id'] = self.company_assignment_id and self.company_assignment_id.id or False
        return res

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        if self.employee_id and self.employee_id.contract_id:
            data = self.employee_id.contract_id
            self.curr_employment_type_id = data.employment_type_id and data.employment_type_id.id or False
            self.curr_employment_status_id = data.employment_status_id and data.employment_status_id.id or False
            self.curr_company_assignment_id = data.company_assignment_id and data.company_assignment_id.id or False
        return super(HREmployeeMovement, self)._onchange_employee_id()
