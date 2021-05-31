# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class HRContract(models.Model):
    _inherit = 'hr.contract'
    _order = 'date_start desc'

    rank_id = fields.Many2one('hr.employee.rank', string="Rank", track_visibility="always")
    job_title = fields.Char(string="Job Title", track_visibility="always")
    employee_number = fields.Char(string="Employee Number", track_visibility="always")
    date_created = fields.Date("Date Created", default=fields.Date.context_today)
    reason_changing = fields.Char("Reason For Changing", default="Starting Contract")
    total_years = fields.Float(string="Total Years", compute='_get_total_years')
    agency_id = fields.Many2one('res.partner', string="Agency")
    duties = fields.Text(string='Duties')
    responsibilities = fields.Text(string='Responsibilities')

    def write(self, vals):
        super(HRContract, self).write(vals)
        if 'state' in vals and vals.get('state'):
            if self.employee_id:
                self.employee_id.compute_employee_contract_record()
        return True

    @api.model
    def create(self, vals):
        res = super(HRContract, self).create(vals)
        res.employee_id.compute_employee_contract_record()
        return res

    def _get_total_years(self):
        for r in self:
            date_start = datetime.strptime(r.date_start.strftime(DT), DT)
            date_end = r.date_end and datetime.strptime(r.date_end.strftime(DT), DT) or datetime.now()
            r.total_years = (date_end - date_start).days / 365.25 or 0

    @api.constrains('resource_calendar_id', 'employee_id')
    def _validate_resource_calendar(self):
        if self.resource_calendar_id and self.employee_id and self.employee_id.contract_id:
            if self.employee_id.contract_id.id == self.id:
                self.employee_id.write({'resource_calendar_id': self.resource_calendar_id.id})

    @api.constrains('state')
    def _validate_state_requirement(self):
        if self.state == 'open':
            if any([not self.employee_id, not self.rank_id, not self.department_id, not self.job_id, not self.employee_number]):
                raise ValidationError(_(
                    'Please make sure that the following fields has a value.\n\tEmployee Name\n\tDepartment\n\tJob Position\n\tRank\n\tEmployee Number'))

    @api.onchange('job_id')
    def _onchange_job_title(self):
        if self.job_id:
            self.job_title = self.job_id.name

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        super(HRContract, self)._onchange_employee_id()
        if self.employee_id:
            self.rank_id = self.employee_id.rank_id and self.employee_id.rank_id.id
            self.employee_number = self.employee_id.employee_number

    def _assign_open_contract_data(self, contract):
        return {
                'job_id': contract.job_id and contract.job_id.id or False,
                'department_id': contract.department_id and contract.department_id.id or False,
                'rank_id': contract.rank_id and contract.rank_id.id or False,
                'job_title': contract.job_title,
                'company_id': contract.company_id and contract.company_id.id or False,
                'employee_number': contract.employee_number,
                'resource_calendar_id': contract.resource_calendar_id.id,
                'agency_id': contract.agency_id and contract.agency_id.id or False,
            }

    def _assign_open_contract(self):
        super(HRContract, self)._assign_open_contract()
        for contract in self:
            contract.employee_id.sudo().write(self._assign_open_contract_data(contract))
