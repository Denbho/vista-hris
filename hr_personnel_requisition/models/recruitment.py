# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError


class HRContract(models.Model):
    _inherit = 'hr.contract'

    wage = fields.Monetary('Wage', required=True, tracking=False, help="Employee's monthly gross wage.")
    employment_type_id = fields.Many2one('hr.employment.type', string="Employment Type", track_visibility="always")
    employment_status_id = fields.Many2one('hr.employment.status', string="Employment Status", track_visibility="always")
    company_assignment_id = fields.Many2one('res.company', string="Company Assignment", track_visibility="always")

    def _assign_open_contract_data(self, contract):
        res = super(HRContract, self)._assign_open_contract_data(contract)
        res['employment_type_id'] = self.employment_type_id and self.employment_type_id.id or False
        res['employment_status_id'] = self.employment_status_id and self.employment_status_id.id or False
        res['company_assignment_id'] = self.company_assignment_id and self.company_assignment_id.id or False
        return res


class EmployeeRequisitionSkill(models.Model):
    _name = 'hr.employee.requisition.skill'
    _description = "Skill level for the requisition"
    _rec_name = 'skill_id'
    _order = "skill_level_id"

    employee_requisition_id = fields.Many2one('hr.personnel.requisition', required=True, ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', required=True)
    skill_level_id = fields.Many2one('hr.skill.level', required=True)
    skill_type_id = fields.Many2one('hr.skill.type', required=True)
    level_progress = fields.Integer(related='skill_level_id.level_progress')

    _sql_constraints = [
        ('_unique_skill', 'unique (employee_requisition_id, skill_id)', "Two levels for the same skill is not allowed"),
    ]

    @api.constrains('skill_id', 'skill_type_id')
    def _check_skill_type(self):
        for record in self:
            if record.skill_id not in record.skill_type_id.skill_ids:
                raise ValidationError(_("The skill %s and skill type %s doesn't match") % (
                    record.skill_id.name, record.skill_type_id.name))

    @api.constrains('skill_type_id', 'skill_level_id')
    def _check_skill_level(self):
        for record in self:
            if record.skill_level_id not in record.skill_type_id.skill_level_ids:
                raise ValidationError(_("The skill level %s is not valid for skill type: %s ") % (
                    record.skill_level_id.name, record.skill_type_id.name))


class HREmploymentType(models.Model):
    _name = 'hr.employment.type'

    name = fields.Char(string="Employment Type", required=True)

class HREmploymentStatus(models.Model):
    _name = 'hr.employment.status'

    name = fields.Char(string="Employment Status", required=True)


class PersonnelRequisition(models.Model):
    _name = "hr.personnel.requisition"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin', 'document.default.approval']

    active = fields.Boolean(default=True)
    name = fields.Char(string="Job Requisition Number.", copy=False,
                       index=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 default=lambda self: self.env.company)
    job_id = fields.Many2one('hr.job', string="Job Position", required=True, track_visibility="always",
                             readonly=True, states={'draft': [('readonly', False)]})
    rank_id = fields.Many2one('hr.employee.rank', string="Rank", track_visibility="always",
                              readonly=True, states={'draft': [('readonly', False)]})
    rank_group_id = fields.Many2one('hr.employee.rank.group', string="Rank Group", store=True,
                                    related="rank_id.rank_group_id")
    department_id = fields.Many2one('hr.department', string="Department", track_visibility="always", required=True,
                                    readonly=True, states={'draft': [('readonly', False)]})
    request_type = fields.Selection([('New', 'Additional/New'),
                                     ('Replacement', 'Replacement')], string="Request Type",
                                    required=True, track_visibility="always",
                                    readonly=True, states={'draft': [('readonly', False)]})
    replacement_employee_id = fields.Many2one('res.partner', string="Employee For Replacement", track_visibility='always',
                                           readonly=True, states={'draft': [('readonly', False)]})
    expected_new_employee = fields.Integer(string="Expected New Employee", required=True, track_visibility='always',
                                           readonly=True, states={'draft': [('readonly', False)]}, default=1)
    target_start_date = fields.Date(string="Target Start Date", help="Target of the the Newly hired employees to start",
                                    readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string="Requisition Justification", help="Reason for the requisition",
                              readonly=True, states={'draft': [('readonly', False)]})
    employment_type_id = fields.Many2one('hr.employment.type', string="Employment Type", required=True,
                                         track_visibility="always", readonly=True,
                                         states={'draft': [('readonly', False)]})
    job_description = fields.Text(string="Job Description", track_visibility='always', required=True,
                                  readonly=True, states={'draft': [('readonly', False)]})
    job_qualification = fields.Text(string="Job Qualification", track_visibility='always', readonly=True, states={'draft': [('readonly', False)]})
    requisition_skill_ids = fields.One2many('hr.employee.requisition.skill', 'employee_requisition_id', string="Skills",
                                            readonly=True, states={'draft': [('readonly', False)]})
    current_headcount = fields.Integer(string="Current Headcount", store=True, compute="_get_current_headcount")
    applicant_ids = fields.One2many('hr.applicant', 'personnel_requisition_id', string="Applicants")
    hiring_status = fields.Selection([('draft', 'Draft'),
                                      ('inprogress', 'In progress'),
                                      ('halted', 'Halted'),
                                      ('done', 'Done'),
                                      ('canceled', 'Canceled')], default='draft', string="Hiring Status",
                                     track_visibility='always', copy=False)
    forced_done = fields.Boolean(string="Forced Done/Closed", copy=False)
    forced_done_user_id = fields.Many2one('res.users', string="Forced Done/Closed By", copy=False)
    done_date = fields.Datetime(string="Date Done/Closed", copy=False)

    total_hired = fields.Integer(string="Hired")
    total_proposed = fields.Integer(string="Proposal")
    total_applicants = fields.Integer(string="Total Applicants")

    total_for_recruitment = fields.Integer(string="For Recruitment", copy=False)
    office_id = fields.Many2one('hr.office.location', string="Office Location", track_visibility="always", required=True,
                                readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('submitted', 'Waiting for Confirmation'),
                              ('confirmed', 'Waiting for Verification'),
                              ('verified', 'Waiting for 1st Approval'),
                              ('approved1', 'Waiting for 2nd Approval'),
                              ('approved2', 'Waiting for Final Approval'),
                              ('approved', 'Approved'),
                              ('canceled', 'Cancelled')], string="Status",
                             default='draft', readonly=True, copy=False, track_visibility="always")
    approved1_by = fields.Many2one('res.users', string="1st Approved By", readonly=True)
    approved1_date = fields.Datetime('1st Approved Date', readonly=True)
    approved2_by = fields.Many2one('res.users', string="2nd Approved By", readonly=True)
    approved2_date = fields.Datetime('2nd Approved Date', readonly=True)
    hr_department_group_id = fields.Many2one("hr.department.group", string="Group", store=True,
                                             compute="_get_department_group")

    @api.depends('department_id', 'department_id.hr_department_group_id')
    def _get_department_group(self):
        for i in self:
            if i.department_id:
                i.hr_department_group_id = i.department_id.hr_department_group_id and i.department_id.hr_department_group_id.id or False

    def unlink(self):
        for r in self:
            if r.state == 'approved':
                raise ValidationError(_('Deletion of approved personnel requisition is not allowed.'))
        return super(PersonnelRequisition, self).unlink()

    @api.depends('job_id')
    def _get_current_headcount(self):
        contract = self.env['hr.contract']
        for r in self:
            r.current_headcount = 0
            if r.job_id:
                r.current_headcount = contract.search_count([('company_id', '=', r.company_id.id),
                                                             ('department_id', '=', r.department_id.id),
                                                             ('job_id', '=', r.job_id.id),
                                                             ('state', 'in', ['open'])])

    @api.constrains('expected_new_employee')
    def _validate_expected_new_employee(self):
        if self.expected_new_employee <= 0:
            raise ValidationError(_("Expected New Employee should greater than or equal to One (1) headcount."))

    def submit_request(self):
        super(PersonnelRequisition, self).submit_request()
        self.write({'name': self.env['ir.sequence'].get('personnel.requisition')})

    def approve1_request(self):
        return self.write({
                    'state': 'approved1',
                    'approved1_by': self._uid,
                    'approved1_date': datetime.now()
                })

    def approve2_request(self):
        return self.write({
                    'state': 'approved2',
                    'approved2_by': self._uid,
                    'approved2_date': datetime.now()
                })

    def approve_request(self):
        self.write({'hiring_status': 'inprogress'})
        return super(PersonnelRequisition, self).approve_request()

    def hiring_force_done(self):
        return self.write({
            'hiring_status': 'done',
            'forced_done': True,
            'forced_done_user_id': self._uid,
            'done_date': datetime.now(),
            'total_for_recruitment': 0
        })

    def hiring_halt(self):
        return self.write({
            'hiring_status': 'halted',
        })

    def hiring_resume(self):
        return self.write({
            'hiring_status': 'inprogress',
        })

    def hiring_cancel(self):
        return self.write({
            'hiring_status': 'canceled',
            'total_for_recruitment': 0
        })

    def cron_update_hiring_status(self):
        data = self.sudo().search([('state', '=', 'approved'), ('hiring_status', 'not in', ['done'])])
        for r in data:
            r.get_hiring_status()

    def get_hiring_status(self):
        applicant = self.env['hr.applicant']
        for r in self:
            total_applicants = 0
            total_hired = 0
            total_proposed = 0
            if not r.hiring_status in [False, 'draft']:
                hired = 0
                proposed = 0
                applicant_records = applicant.sudo().search([
                    ('personnel_requisition_id', '=', r.id),
                    # ('contract_id', 'not in', [False])
                ])
                for rec in applicant_records:
                    if rec.contract_id:
                        if rec.contract_id.state == 'draft':
                            proposed += 1
                        elif rec.contract_id.state == 'cancel' and not rec.contract_id.date_end:
                            proposed += 1
                        else:
                            hired += 1
                if r.expected_new_employee == hired and not r.hiring_status in ['done']:
                    r.write({
                        'hiring_status': 'done',
                        'done_date': datetime.now(),
                        'forced_done': False,
                        'forced_done_user_id': False,
                        'total_for_recruitment': 0
                    })
                if r.expected_new_employee != hired and not r.hiring_status in ['done'] and (
                        r.expected_new_employee - hired) != r.total_for_recruitment:
                    r.write({
                        'total_for_recruitment': r.expected_new_employee - hired
                    })

                r.write({
                    'total_applicants': len(applicant_records.ids),
                    'total_hired': hired,
                    'total_proposed': proposed
                })
        return True


class HRJob(models.Model):
    _inherit = "hr.job"

    state = fields.Selection([
        ('recruit', 'Recruitment in Progress'),
        ('open', 'Not Recruiting')
    ], string='Status', store=True, tracking=True, copy=False, default='open',
        compute='_get_recruitment_status', inverse='_inverse_get_recruitment_status',
        help="Set whether the recruitment process is open or closed for this job position.")
    personnel_requisition_ids = fields.One2many('hr.personnel.requisition', 'job_id', string="Personnel Requisitions")

    @api.depends('personnel_requisition_ids', 'personnel_requisition_ids.hiring_status',
                 'personnel_requisition_ids.total_for_recruitment')
    def _get_recruitment_status(self):
        for r in self:
            no_of_recruitment = 0
            r.state = 'open'
            for rec in r.personnel_requisition_ids:
                no_of_recruitment += rec.total_for_recruitment
                if rec.hiring_status == 'inprogress' and rec.active:
                    r.state = 'recruit'
                    # break
            r.write({'no_of_recruitment': no_of_recruitment})

    def _inverse_get_recruitment_status(self):
        for i in self:
            continue


class HRRecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    create_employee = fields.Boolean(string="Create Employee")
    create_contract = fields.Boolean(string="Create Contract")


class HRApplicant(models.Model):
    _inherit = 'hr.applicant'

    # firstname = fields.Char(string="First Name", tracking=True)
    # lastname = fields.Char(string="Last Name", tracking=True)
    # middle_name = fields.Char(string="Middle Name", tracking=True)
    # nick_name = fields.Char(string="Nick Name (AKA)", tracking=True)
    # suffix_name = fields.Char(string="Suffix Name", tracking=True)

    stage_create_employee = fields.Boolean(string="Create Employee", store=True, compute='_get_stage_data')
    stage_create_contract = fields.Boolean(string="Create Contract", store=True, compute='_get_stage_data')
    personnel_requisition_id = fields.Many2one('hr.personnel.requisition', string="Personnel Requisition")
    contract_id = fields.Many2one('hr.contract', string="Proposed Contract")
    job_id = fields.Many2one('hr.job', "Applied Job",
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('state', '=', 'recruit')]")
    personnel_requisition_id = fields.Many2one('hr.personnel.requisition', string="Personnel Requisition",
                                               domain="[('company_id', 'in', [False, company_id]), ('job_id', '=', job_id), ('hiring_status', '=', 'inprogress')]")
    employment_type_id = fields.Many2one('hr.employment.type', string="Employment Type", store=True, related="personnel_requisition_id.employment_type_id")
    office_id = fields.Many2one('hr.office.location', string="Office Location", store=True, related="personnel_requisition_id.office_id")
    hr_department_group_id = fields.Many2one("hr.department.group", string="Group", store=True,
                                             compute="_get_department_group")

    @api.depends('department_id', 'department_id.hr_department_group_id')
    def _get_department_group(self):
        for i in self:
            if i.department_id:
                i.hr_department_group_id = i.department_id.hr_department_group_id and i.department_id.hr_department_group_id.id or False

    @api.onchange('personnel_requisition_id')
    def _onchange_personnel_requisition_id(self):
        for r in self:
            if r.personnel_requisition_id:
                r.department_id = r.personnel_requisition_id.department_id.id

    @api.constrains('stage_id', 'stage_id.create_employee', 'stage_id.create_contract')
    def _get_stage_data(self):
        for r in self:
            if r.stage_id:
                r.stage_create_employee = r.stage_id.create_employee
                r.stage_create_contract = r.stage_id.create_contract

    def contract_data(self):
        data = {
            'name': f"{self.job_id.name}: {self.partner_name}",
            'job_id': self.job_id.id,
            'job_title': self.job_id.name,
            'department_id': self.personnel_requisition_id.department_id.id,
            'resource_calendar_id': self.personnel_requisition_id.company_id.resource_calendar_id.id,
            'date_start': self.availability,
            'rank_id': self.personnel_requisition_id.rank_id.id,
            'employment_type_id': self.personnel_requisition_id.employment_type_id and self.personnel_requisition_id.employment_type_id.id or False,
            'wage': self.salary_proposed,
            'state': 'draft'
        }
        return data

    def create_draft_contract(self):
        """ Create an hr.contract from the hr.applicants for proposal"""
        contract = False
        if not self.contract_id:
            contract = self.env['hr.contract'].create(self.contract_data())
            self.write({'contract_id': contract.id})
        else:
            contract = self.contract_id
        contract_action = self.env.ref('hr_personnel_requisition.hr_contract_proposal_action_form')
        dict_act_window = contract_action.read([])[0]
        dict_act_window['context'] = {'form_view_initial_mode': 'edit'}
        dict_act_window['res_id'] = contract.id
        return dict_act_window

    def update_employee_contract_data(self, employee):
        return {
            'employee_id': employee.id,
            'employee_number': employee.employee_number,
            'state': 'open'
        }

    def update_employee_data(self):
        verbal = 0
        numerical = 0
        abstract = 0
        for exam_line in self.examination_result_ids:
            if exam_line.category == 'Iq':
                if exam_line.iq_type == 'Verbal':
                    verbal = exam_line.rate
                elif exam_line.iq_type == 'Numerical':
                    numerical = exam_line.rate
                elif exam_line.iq_type == 'Abstract':
                    abstract = exam_line.rate
        return {
            'application_id': self.id,
            'application_remark': self.description,
            'application_date': datetime.strftime(self.create_date, "%Y-%m-%d"),
            'recruitment_date': date.today(),
            'employment_type_id': self.personnel_requisition_id.employment_type_id and self.personnel_requisition_id.employment_type_id.id or False,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'office_id': self.office_id and self.office_id.id or False,
            'verbal': verbal,
            'numerical': numerical,
            'abstract': abstract,
        }

    def create_employee_from_applicant(self):
        res = super(HRApplicant, self).create_employee_from_applicant()
        if self.emp_id:
            self.emp_id.write(self.update_employee_data())
        if self.contract_id and self.emp_id:
            self.contract_id.write(self.update_employee_contract_data(self.emp_id))
            self.contract_id._assign_open_contract()
        return res
