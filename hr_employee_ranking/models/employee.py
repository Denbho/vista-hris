# -*- coding: utf-8 -*-
from odoo import fields, models, api


class HREmployeeRankGroup(models.Model):
    _name = 'hr.employee.rank.group'
    _description = 'Employee Rank Group'
    _order = 'sequence'

    name = fields.Char(string="Group Name", required=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(string="Description")


class HREmployeeRank(models.Model):
    _name = 'hr.employee.rank'
    _description = 'Employee Rank'
    _order = 'sequence'

    name = fields.Char(string="Group Name", required=True)
    rank_group_id = fields.Many2one('hr.employee.rank.group', string="Rank Group", required=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(string="Description")


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    rank_id = fields.Many2one('hr.employee.rank', string="Rank", track_visibility="always")
    rank_group_id = fields.Many2one('hr.employee.rank.group', string="Rank Group", store=True,
                                    related="rank_id.rank_group_id")