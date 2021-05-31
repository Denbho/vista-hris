# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResRegionCluster(models.Model):
    _name = 'res.region.cluster'
    _description = 'Area Cluster'

    name = fields.Char(string="Cluster Name", required=True)


class HRDivisionAssignment(models.Model):
    _name = 'hr.division.assignment'
    _description = 'Division Assignment'

    name = fields.Char(string="Division Name", required=True)


class HREmployeeProjectArea(models.Model):
    _name = 'hr.employee.project.area'
    _description = 'Employee Project Area'

    name = fields.Char(string="Project Area", required=True)
    cluster_id = fields.Many2one('res.region.cluster', string="Cluster", required=True)
    division_id = fields.Many2one('hr.division.assignment', string="Division", required=True)


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    project_area_id = fields.Many2one('hr.employee.project.area', string="Project Area")
    cluster_id = fields.Many2one('res.region.cluster', string="Cluster",
                                 store=True, related="project_area_id.cluster_id")
    division_id = fields.Many2one('hr.division.assignment', string="Division", store=True, related="project_area_id.division_id")