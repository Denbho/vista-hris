# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime, date


class HREmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'utm.mixin']

    def _compute_iq_average(self):
        for record in self:
            record.iq_average = ((record.verbal+record.numerical+record.abstract)/300)*100

    application_id = fields.Many2one('hr.applicant', string="Application/Recruitement Source", copy=False)
    employment_type_id = fields.Many2one('hr.employment.type', string="Employment Type", track_visibility="always")
    employment_status_id = fields.Many2one('hr.employment.status', string="Employment Status", track_visibility="always")
    company_assignment_id = fields.Many2one('res.company', string="Company Assignment", track_visibility="always")
    application_remark = fields.Text(string="Remarks", copy=False)
    application_date = fields.Date(string="Application Date", copy=False)
    recruitment_date = fields.Date(string="Recruitment Date", copy=False)
    onboarding_date = fields.Date(string="Onboarding Date", copy=False)
    verbal = fields.Float(string="Verbal", track_visibility="always")
    numerical = fields.Float(string="Numerical", track_visibility="always")
    abstract = fields.Float(string="Abstract", track_visibility="always")
    iq_average = fields.Float(string="IQ Average", compute='_compute_iq_average')
    gpa = fields.Float(string="GPA", track_visibility="always")
    prc = fields.Char(string="PRC", track_visibility="always")
    rating = fields.Float(string="Rating", track_visibility="always")
    sss = fields.Char(string="SSS", track_visibility="always")
    hdmf = fields.Char(string="HDMF", track_visibility="always")
    philhealth = fields.Char(string="Philhealth", track_visibility="always")
    gsis = fields.Char(string="GSIS", track_visibility="always")
    tin = fields.Char(string="TIN", track_visibility="always")
