# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class HRDocumentChecklist(models.Model):
    _name = 'hr.document.checklist'
    _description = 'Document Checklist'

    name = fields.Char(string="Document Name")
    required_pre_employment_requirement = fields.Boolean(string="Required", help="Required before converting applicant to employee.")
    active = fields.Boolean()


class HRApplicant(models.Model):
    _inherit = 'hr.applicant'

    document_requirement_ids = fields.Many2many('hr.document.checklist', 'application_document_req_rel', string="Document List")

    def update_employee_data(self):
        res = super(HRApplicant, self).update_employee_data()
        res['document_requirement_ids'] = self.document_requirement_ids.ids
        return res

    def create_employee_from_applicant(self):
        required_doc = self.env['hr.document.checklist'].search([('active', '=', True), ('required_pre_employment_requirement', '=', True)])
        msg = ''
        for r in required_doc:
            if not r.id in self.document_requirement_ids.ids:
                msg += f"\t{r.name}\n"
        if msg != '':
            raise ValidationError(_(f"The following documents should be submitted before converting applicant to employee: \n\n{msg}"))
        return super(HRApplicant, self).create_employee_from_applicant()


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    document_requirement_ids = fields.Many2many('hr.document.checklist', 'employee_document_req_rel', string="Document List")