# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
import logging

_logger = logging.getLogger(__name__)

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    contract_history_ids = fields.Many2many('hr.contract', 'employee_contract_movement_rel', string="Contract History")
    tenure_year = fields.Float(string="Total Years of Tenure")
    tenure_display = fields.Char(string="Tenure")
    parent_id = fields.Many2one('hr.employee', 'Manager')
    agency_id = fields.Many2one('res.partner', string="Agency")
    awards = fields.Char(string="Awards")

    def compute_employee_contract_record(self):
        for i in self:
            contract = self.env['hr.contract'].search([('employee_id', '=', self.id),
                                                       ('state', 'not in', ['draft', False])], order='date_start desc')
            # i.contract_history_ids = contract.ids
            tenure = sum(contract.mapped('total_years'))
            i.tenure_year = tenure
            year = int(tenure)
            month = int(tenure % 1 * 12)
            tenure_display = f"{int(tenure)} year/s"
            if month:
                tenure_display += f", and {month} month/s"
            # i.tenure_display = tenure_display
            i.write({'tenure_year': tenure, 'tenure_display': tenure_display, 'contract_history_ids': contract.ids})

    def cron_compute_year_of_tenure(self):
        employee = self.env['hr.employee'].search([('contract_id.state', '=', 'open')])
        for r in employee:
            r.compute_employee_contract_record()



class HREmployeeMovement(models.Model):
    _name = "hr.employee.movement"
    _description = "Employee Management"
    _inherit = ["mail.thread", "mail.activity.mixin", "resource.mixin", "document.default.approval"]
    _check_company_auto = True

    name = fields.Char(string="Reference", default="/", copy=False)
    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True, track_visibility="always",
                                  readonly=True, states={'draft': [('readonly', False)]}, index=True)
    commended_by_employee_id = fields.Many2one('hr.employee', string="Commended By", track_visibility="always",
                                  readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string="Company")
    department_id = fields.Many2one('hr.department', string="Department")
    job_id = fields.Many2one('hr.job', string="Job Position")
    rank_id = fields.Many2one('hr.employee.rank', string="Rank")
    job_title = fields.Char(string="Job Title")
    employee_number = fields.Char(string="Employee Number", track_visibility="always")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    movement_type = fields.Selection([
                            ('promotion', 'Promotion'),
                            # ('demotion', 'Demotion'),
                            ('lateral', 'Lateral Transfer'),
                            ('promotion_lateral', 'Lateral Transfer + Promotion'),
                            # ('demotion_lateral', 'Lateral Transfer + Demotion'),
                            ], string="Movement Type", required=True, track_visibility="always",
                        readonly=True, states={'draft': [('readonly', False)]})
    movement_process_date = fields.Date(string="Movement Date", required=True,
                                        track_visibility="always", default=fields.Date.context_today,
                                        readonly=True, states={'draft': [('readonly', False)]})
    new_employee_number = fields.Char(string="New Employee Number", track_visibility="always")
    effectivity_date = fields.Date(string="Effectivity Date", track_visibility="always",
                                   readonly=False, states={'approved': [('readonly', True)]})
    new_job_id = fields.Many2one('hr.job', string='New Job Position', track_visibility="always",
                                 readonly=True, states={'draft': [('readonly', False)]})
    new_job_title = fields.Char(string="New Job Title", track_visibility="always",
                                readonly=True, states={'draft': [('readonly', False)]})
    new_rank_id = fields.Many2one('hr.employee.rank', string="New Rank", track_visibility="always",
                                  readonly=True, states={'draft': [('readonly', False)]})
    new_department_id = fields.Many2one('hr.department', string="New Department", track_visibility="always",
                                        readonly=True, states={'draft': [('readonly', False)]})
    new_company_id = fields.Many2one('res.company', string="New Company", track_visibility="always",
                                     readonly=True, states={'draft': [('readonly', False)]})
    new_contract_id = fields.Many2one('hr.contract', string="New Contract", readonly=True)
    contract_history_ids = fields.Many2many('hr.contract', 'contract_movement_rel', string="Contract History",
                                compute='_compute_contract_history_record', store=True)
    duties = fields.Text(string='Duties', readonly=True, states={'draft': [('readonly', False)]})
    responsibilities = fields.Text(string='Responsibilities', readonly=True, states={'draft': [('readonly', False)]})

    def submit_request(self):
        super(HREmployeeMovement, self).submit_request()
        self.write({'name': self.env['ir.sequence'].get('employee.movement')})

    @api.depends('employee_id')
    def _compute_contract_history_record(self):
        for i in self:
            contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                       ('state', 'not in', ['draft', False])])
            i.contract_history_ids = contract.ids

    @api.constrains('contract_id')
    def _validate_movement_data(self):
        if not self.contract_id:
            raise ValidationError(_("The selected employee has no valid contract record"))

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        if self.employee_id and self.employee_id.contract_id:
            data = self.employee_id.contract_id
            self.department_id = data.department_id.id
            self.job_id = data.job_id.id
            self.job_title = data.job_title or (data.job_id.name or '')
            self.rank_id = data.rank_id.id or False
            self.company_id = data.company_id.id
            self.new_company_id = data.company_id.id
            self.contract_id = data.id or False
            self.employee_number = data.employee_number
            self.new_employee_number = data.employee_number

    def close_existing_open_contract(self, contract):
        return contract.sudo().write({
            'date_end': self.effectivity_date,
            'state': 'cancel',
            'reason_changing': dict(self._fields['movement_type'].selection).get(self.movement_type)
        })

    def cron_set_contract_running(self):
        data = self.search([('effectivity_date', '=', date.today()), ('state', '=', 'approved')])
        for r in data:
            if r.new_contract_id.state in ['draft', 'close']:
                if r.contract_id.state == 'open':
                    r.close_existing_open_contract(r.contract_id)
                r.new_contract_id.write({'state': 'open'})
                r.new_contract_id._assign_open_contract()

    def set_open_employee_contract(self):
        if self.contract_id.state == 'open':
            self.close_existing_open_contract(self.employee_id.contract_id)
        self.new_contract_id.write({'state': 'open'})
        self.new_contract_id._assign_open_contract()

    def contract_data(self):
        return {
                'name': f"{self.employee_id.name} - [{self.job_id.name}]",
                'employee_id': self.employee_id.id,
                'employee_number': self.employee_number,
                'job_id': self.new_job_id and self.new_job_id.id or (self.job_id and self.job_id.id),
                'job_title': self.new_job_title or self.job_title,
                'rank_id': self.new_rank_id.id or self.rank_id.id,
                'department_id': self.new_department_id.id or self.department_id.id,
                'company_id': self.new_company_id.id or self.comp,
                'date_start': self.effectivity_date,
                'date_created': date.today(),
                'wage': self.contract_id.wage,
                'state': 'draft',
                'active': True,
                'duties': self.duties,
                'responsibilities': self.responsibilities,
            }

    def approve_request(self):
        contract = self.env['hr.contract']
        if not self.effectivity_date:
            raise ValidationError(_("Please input effectivity date."))
        new_contract = contract.sudo().create(self.contract_data())
        self.write({
            'new_contract_id': new_contract.id,
            'state': 'approved',
            'approved_by': self._uid,
            'approved_date': datetime.now()
        })
        if self.effectivity_date <= date.today():
            self.set_open_employee_contract()
        return super(HREmployeeMovement, self).approve_request()
