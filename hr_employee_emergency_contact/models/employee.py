from odoo import fields, models, api, _


class EmergencyContact(models.Model):
    _name = 'emergency.contact'
    _description = 'Emergency Contact'

    name = fields.Char(string="Contact", required=True)
    email = fields.Char(string="Email")
    mobile = fields.Char(string="Mobile")
    relationship = fields.Char(string="Relationship")
    employee_id = fields.Many2one("hr.employee", string="Employee")


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    emergency_contact_ids = fields.One2many('emergency.contact', 'employee_id')
