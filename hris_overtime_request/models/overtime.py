# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from datetime import datetime, date

_STATES = [
    ('draft', 'Draft'),
    ('to_confirm', 'Waiting for confirmation'),
    ('to_approve', 'Waiting for approval'),
    ('approved', 'Approved'),
    ('verify', 'Waiting to Verify'),
    ('verified', 'Verified'),
    ('rejected', 'Rejected/Canceled')
]


class Request_OvertimeApp(models.Model):
    _name = 'request.overtime.app'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _description = 'Request Overtime'

    def _get_employee_domain(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        domain = [('id', '=', employee.id)]
        if self.env.user.has_group('hr.group_hr_user'):
            domain = []
        return domain

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.onchange('employee_id')
    def _get_defaults(self):
        for rec in self:
            if rec.employee_id:
                rec.update({
                    'department_id': rec.employee_id.department_id.id,
                    'job_id': rec.employee_id.job_id.id,
                    'manager_id': rec.sudo().employee_id.parent_id.user_id.id,
                })

    name = fields.Char('Request Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee Name',
                                  domain=_get_employee_domain, default=lambda self: self.env.user.employee_id.id,
                                  required=True, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string="Department",
                                    related="employee_id.department_id", track_visibility='onchange')
    job_id = fields.Many2one('hr.job', string="Job Position", related="employee_id.job_id", track_visibility='onchange')
    manager_id = fields.Many2one('res.users', string="Manager",
                                 related="employee_id.parent_id.user_id", store=True, track_visibility='onchange')
    current_user = fields.Many2one('res.users', string="Current User",
                                   related='employee_id.user_id',
                                   default=lambda self: self.env.uid, track_visibility='onchange',
                                   store=True)
    current_user_boolean = fields.Boolean()
    responsible_id = fields.Many2one('res.users', related='employee_id.responsible_id.user_id', store=True,
                                     readonly=True, string="Team Lead")
    date_filling = fields.Date(string='Date Filing', track_visibility='onchange', default=fields.Date.context_today,
                             required=True, readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(string="Requested Date For OT", track_visibility='onchange', default=fields.Date.context_today,
                       required=True, readonly=True, states={'draft': [('readonly', False)]})
    time_from = fields.Float(string="Time In", required=True, readonly=True, states={'draft': [('readonly', False)]})
    time_to = fields.Float(string="Time Out", required=True, readonly=True, states={'draft': [('readonly', False)]})
    no_of_hours = fields.Float(string="No. of hours", compute='_get_hours', store=True)

    actual_time_start = fields.Float(string="Actual Time Start", copy=False, states={'verified': [('readonly', True)]})
    actual_time_end = fields.Float(string="Actual Time End", copy=False, states={'verified': [('readonly', True)]})
    actual_total = fields.Float(string="Actual Hours", compute='_get_actual_hours')
    work_to_perform = fields.Text(string="Work to Perform", required=True, readonly=True, states={'draft': [('readonly', False)]})
    work_performed = fields.Text(string="Work Performed", states={'verified': [('readonly', True)]}, copy=False)
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')

    def button_draft(self):
        for rec in self:
            rec.state = 'draft'
        return True

    def button_to_approve(self):
        for rec in self:
            rec.state = 'to_confirm'
        return True

    def button_confirm(self):
        for rec in self:
            rec.name = self.env['ir.sequence'].get('request.overtime.app')
            rec.state = 'to_approve'
        return True

    def button_approved(self):
        for rec in self:
            rec.state = 'approved'
        return True

    def button_to_verify(self):
        for rec in self:
            rec.state = 'verify'
        return True

    def button_to_verified(self):
        for rec in self:
            rec.state = 'verified'
            if date.today() < rec.date:
                raise ValidationError(_("You can not verify OT Hours that has not rendered yet."))
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Overtime Application is Verified!',
                    'type': 'rainbow_man',
                }
            }
        return True

    def button_rejected(self):
        for rec in self:
            rec.state = 'rejected'
        return True

    def unlink(self):
        for request in self:
            if not request.state == 'rejected':
                raise UserError('In order to delete OVERTIME REQUEST, you must CANCEL it first.')
        return super(Request_OvertimeApp, self).unlink()

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({
            'state': 'draft',
            'name': self.env['ir.sequence'].get('request.overtime.app'),
        })
        return super(Request_OvertimeApp, self).copy(default)

    @api.depends('time_from', 'time_to')
    def _get_hours(self):
        for r in self:
            if r.time_to > r.time_from:
                r.no_of_hours = r.time_to - r.time_from
            else:
                time_total = 24 - r.time_from
                time_total += r.time_to
                r.no_of_hours = time_total

    @api.depends('actual_time_start', 'actual_time_end')
    def _get_actual_hours(self):
        for r in self:
            if r.actual_time_end > r.actual_time_start:
                r.actual_total = r.actual_time_end - r.actual_time_start
            else:
                time_total = 24 - r.actual_time_start
                time_total += r.actual_time_end
                r.actual_total = time_total

    @api.constrains('actual_total', 'no_of_hours')
    def validate_actual_hours(self):
        if self.actual_total > self.no_of_hours:
            raise ValidationError(_("Actual rendered hours should be less than or equal to approved overtime hours."))

    @api.onchange('time_from', 'time_to')
    def _onchange_time(self):
        self.actual_time_start = self.time_from
        self.actual_time_end = self.time_to

    @api.constrains('time_from', 'time_to', 'actual_time_end', 'actual_time_start')
    def _get_valid_hours(self):
        if any([self.time_from > 24, self.time_to > 24, self.actual_time_end > 24, self.actual_time_start > 24, self.actual_time_end == self.actual_time_start, self.time_from == self.time_to]):
            raise ValidationError(_('Time should be in 24 hours format.'))


class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    responsible_id = fields.Many2one('hr.employee', string="Team Lead")
