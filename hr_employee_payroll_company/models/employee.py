# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HREmployeeMovement(models.Model):
    _inherit = "hr.employee.movement"

    payroll_company_id = fields.Many2one('res.company', string="Payroll Company")
    new_payroll_company_id = fields.Many2one('res.company', string="Payroll Company" )

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        super(HREmployeeMovement, self)._onchange_employee_id()
        if self.employee_id and self.employee_id.contract_id:
            data = self.employee_id.contract_id
            self.payroll_company_id = data.payroll_company_id.id
            self.new_payroll_company_id = data.payroll_company_id.id

    def contract_data(self):
        res = super(HREmployeeMovement, self).contract_data()
        res['payroll_company_id'] = self.new_payroll_company_id.id
        return res


class HRContract(models.Model):
    _inherit = 'hr.contract'

    payroll_company_id = fields.Many2one('res.company', string="Payroll Company", store=True, track_visibility='always',
                                         compute='_get_payroll_company', inverse='_inverse_get_payroll_company')

    def _inverse_get_payroll_company(self):
        for r in self:
            continue

    @api.depends('company_id')
    def _get_payroll_company(self):
        for r in self:
            if r.company_id:
                r.payroll_company_id = r.company_id.id

    @api.constrains('state')
    def _validate_payroll_company(self):
        if self.state == 'open' and not self.payroll_company_id:
            raise ValidationError(_("Please make sure to select Payroll Company"))


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        super(HRContract, self)._onchange_employee_id()
        if self.employee_id:
            self.payroll_company_id = self.employee_id.payroll_company_id and self.employee_id.payroll_company_id.id

    def _assign_open_contract_data(self, contract):
        res = super(HRContract, self)._assign_open_contract_data(contract)
        res['payroll_company_id'] = contract.payroll_company_id.id
        return res


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    payroll_company_id = fields.Many2one('res.company', string="Payroll Company")
