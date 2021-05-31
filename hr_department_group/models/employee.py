# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class HRDepartmentGroup(models.Model):
    _name = "hr.department.group"

    name = fields.Char(string="Group Name", required=True)
    description = fields.Text(string="Description")


class HRDepartment(models.Model):
    _inherit = "hr.department"

    hr_department_group_id = fields.Many2one("hr.department.group", string="Group", store=True,
                                             compute="_get_department_group", inverse="_inverse_get_department_group")

    @api.depends("parent_id", "parent_id.hr_department_group_id")
    def _get_department_group(self):
        for i in self:
            if i.parent_id:
                if i.parent_id.hr_department_group_id:
                    i.hr_department_group_id = i.parent_id.hr_department_group_id.id

    def _inverse_get_department_group(self):
        for i in self:
            if not i.parent_id:
                continue


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    hr_department_group_id = fields.Many2one("hr.department.group", string="Group", store=True,
                                             compute="_get_department_group")

    @api.depends('department_id', 'department_id.hr_department_group_id')
    def _get_department_group(self):
        for i in self:
            if i.department_id:
                i.hr_department_group_id = i.department_id.hr_department_group_id and i.department_id.hr_department_group_id.id or False
