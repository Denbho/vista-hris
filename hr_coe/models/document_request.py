from odoo import fields, models, api


class HRDocumentRequest(models.Model):
    _name = 'hr.document.request'
    _description = 'Document Request'
    _inherit = ['employee.certificate']

    def submit_request(self):
        self.write({'name': self.env['ir.sequence'].get('hr.document.request')})
        super(HRDocumentRequest, self).submit_request()
