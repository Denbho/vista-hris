# -*- coding: utf-8 -*-
from odoo import fields, models, api


class HRDocumentRequirement(models.Model):
    _name = 'hr.document.requirement'
    _description = 'Document Requirements Checklist'

    name = fields.Char(string="Document Name")


class HRLicensesAndCertification(models.Model):
    _name = 'hr.license.certification'
    _inherit = ["mail.thread", "mail.activity.mixin", "resource.mixin"]

    employee_id = fields.Many2one('hr.employee', string="Employee")
    type = fields.Char(string="Type", required=True)
    name = fields.Char(string="Number", required=True)
    category = fields.Selection([('license', 'License'), ('certificate', 'Certificate')],
                                string="Category", required=True)
    rating = fields.Float(string="Rating")
    issue_date = fields.Date(string="Issuance Date", required=True)
    location = fields.Char(string="Location", help="Issuance Locations")
    expiry_date = fields.Date(string="Expiry Date")
    with_expiry_date = fields.Boolean(help="Check if this document expires")
    with_rating = fields.Boolean(help="Check if this document has rating")


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    document_requirement_ids = fields.Many2many('hr.document.requirement', 'employee_document_requirement_rel',
                                                string="Document Requirements", track_visibility="always")
    sss = fields.Char('SSS', help="Social Security System")
    hdmf = fields.Char('HDMF', help="Pagibig")
    philhealth = fields.Char('PhilHealth')
    gsis = fields.Char('GSIS')
    tin = fields.Char('TIN', help="Tax Identification Number")
    certificate_license_ids = fields.One2many('hr.license.certification', 'employee_id', string="Certificates and Licenses")
