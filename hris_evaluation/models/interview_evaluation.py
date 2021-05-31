# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


_RATES = [
        ('five', '5'),
        ('four', '4'),
        ('three', '3'),
        ('two', '2'),
        ('one', '1')
    ]


class HRApplicant(models.Model):
    _inherit = 'hr.applicant'

    examination_result_ids = fields.One2many('hr.application.examination.result', 'hr_applicant_id',
                                             string="Examination Results")


class HRApplicantExaminationResult(models.Model):
    _name = 'hr.application.examination.result'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _rec_name = 'category'

    hr_applicant_id = fields.Many2one('hr.applicant', string="Application")
    category = fields.Selection([('Iq', 'IQ Test'), ('Essay', 'Essay')], string="Category",
                                required=True, track_visibility="always")
    iq_type = fields.Selection([('Verbal', 'Verbal'), ('Numerical', 'Numerical'), ('Abstract', 'Abstract')],
                               string="Type", track_visibility="always")
    rate = fields.Float(string="Rating", required=True, track_visibility="always")
    result = fields.Selection([('Passed', 'Passed'), ('Failed', 'Failed')], string="Result",
                              required=True, track_visibility="always")
    comment = fields.Text(track_visibility="always", string="Comments")
    reference_link = fields.Char(string="Reference")


class InterviewEvaluation(models.Model):
    _name = 'hris.interview.evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _rec_name = 'hr_applicant_id'

    hr_applicant_id = fields.Many2one('hr.applicant', string="Application", store=True, required=True, track_visibility="always")
    applicant_name = fields.Char('Name', store=True, related='hr_applicant_id.partner_name')
    job_id = fields.Many2one('hr.job', related='hr_applicant_id.job_id', string="Position Applied for", readonly=True)
    company_id = fields.Many2one('res.company', related='hr_applicant_id.company_id', string="Company", store=True,
                                 readonly=True)
    department_id = fields.Many2one('hr.department', related='hr_applicant_id.department_id', string="Department",
                                    readonly=True)
    f_apperance = fields.Selection(_RATES, default=False, required=True)
    f_apperance_comment = fields.Text(track_visibility="always")
    f_grooming = fields.Selection(_RATES, default=False, required=True, track_visibility="always")
    f_grooming_comment = fields.Text(track_visibility="always")
    f_impact = fields.Selection(_RATES, default=False, required=True, track_visibility="always")
    f_impact_comment = fields.Text(track_visibility="always")
    f_oral = fields.Selection(_RATES, default=False, required=True, track_visibility="always")
    f_oral_comment = fields.Text(track_visibility="always")
    f_mental = fields.Selection(_RATES, default=False, required=True, track_visibility="always")
    f_mental_comment = fields.Text(track_visibility="always")
    f_ambition = fields.Selection(_RATES, default=False, required=True, track_visibility="always")
    f_ambition_comment = fields.Text(track_visibility="always")
    f_interest = fields.Selection(_RATES, default=False, required=True, track_visibility="always")
    f_interest_comment = fields.Text(track_visibility="always")
    f_motivation = fields.Selection(_RATES, default=False, required=True, track_visibility="always")
    f_motivation_comment = fields.Text(track_visibility="always")
    f_standard = fields.Selection(_RATES, default=False, required=True, track_visibility="always")
    f_standard_comment = fields.Text(track_visibility="always")
    f_tech_skills = fields.Selection(_RATES, default=False, required=True, track_visibility="always")
    f_tech_skills_comment = fields.Text(track_visibility="always")
    f_comments = fields.Text(string="Comments", track_visibility="always")
    f_interviewed = fields.Many2one('res.users', string="Interviewed by:")
    f_signature = fields.Binary(string="Signature")
    f_date = fields.Datetime(string='Date', default=datetime.today(), track_visibility="always")
    f_suitable = fields.Boolean('Applicant is suitable', track_visibility="always")
    f_not_suitable = fields.Boolean('Applicant is not suitable', track_visibility="always")
    f_hold = fields.Boolean('Hold for future reference', track_visibility="always")
    f_lst_comments = fields.Text('Other Comments', track_visibility="always")

    evaluator_employee_id = fields.Many2one('hr.employee', string="Evaluator", required=True,
                                            default=lambda self: self.env.user.employee_id.id)
    evaluator_department_id = fields.Many2one('hr.department', string="Department", store=True,
                                              related="evaluator_employee_id.department_id")
    evaluator_job_id = fields.Many2one('hr.job', string="Position", store=True,
                                              related="evaluator_employee_id.job_id")
    evaluator_user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user.id)

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
