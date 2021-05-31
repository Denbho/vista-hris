from odoo import fields, models, api
from datetime import date, datetime


class HealthCondition(models.Model):
    _name = 'health.condition'
    _order = 'date desc'

    employee_id = fields.Many2one('hr.employee')
    health_condition = fields.Char(string="Health Condition", required=True)
    doctor_name = fields.Char(string="Name of the Doctor")
    address = fields.Char(string="Address")
    medications = fields.Text(string="Medications")
    medical_documents = fields.Binary()
    date = fields.Date(string="Date")
    fit_to_work = fields.Boolean()


class HREmployeeDependents(models.Model):
    _name = 'hr.employee.dependents'

    employee_id = fields.Many2one('hr.employee')
    name = fields.Char(string="Dependent", required=True)
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age", compute="_get_dependent_age")
    relationship = fields.Char(string="Relationship", required=True)
    covered = fields.Boolean(string="Covered", default=True)

    def _get_dependent_age(self):
        for r in self:
            if r.date_of_birth.year:
                r.age = date.today().year - r.date_of_birth.year


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    # fit_to_work = fields.Boolean()
    currency_id = fields.Many2one('res.currency', string="Currency", related="company_id.currency_id")
    annual_physical_exam = fields.Selection([
                        ('class_A', 'Class A'),
                        ('class_B', 'Class B'),
                        ('class_C', 'Class C'),
                        ('not_fit_to_work', 'Not Fit to Work')
                    ], string="APE", help="Annual Physical Examination Result", track_visibility="always")
    height = fields.Char(string="Height")
    height_uom = fields.Selection([
                        ('cm', 'cm'),
                        ('ft', 'ft')
                    ], string="Height UOM")
    weight = fields.Float(string="Weight")
    weight_uom = fields.Selection([
                    ('lbs', 'lbs'),
                    ('kg', 'kg')
                ], string="Weight UOM")
    blood_type = fields.Selection([
                    ('A+', 'A+'),
                    ('A-', 'A-'),
                    ('B+', 'B+'),
                    ('B-', 'B-'),
                    ('O+', 'O+'),
                    ('O-', 'O-'),
                    ('AB+', 'AB+'),
                    ('AB-', 'AB-')
                ], string="Blood Type")
    drug_test = fields.Selection([
                    ('Positive', 'Positive'),
                    ('Negative', 'Negative')
                ], String="Drug Test", track_visibility="always")
    health_card_provider = fields.Char(string="Health Card Provider", track_visibility="always")
    health_card_number = fields.Char(string="Card Number", track_visibility="always")
    cap_limit = fields.Monetary(string="Cap Limit", track_visibility="always")
    credit_usage = fields.Monetary(string="Credit Usage", track_visibility="always")
    hmo_validity_date = fields.Date(string='HMO Validity From', track_visibility="always")
    hmo_validity_date_end = fields.Date(string='HMO Validity To', track_visibility="always")
    hmo_coverage = fields.Text(string="Coverage")
    renewal_date = fields.Date(string="Renewal Data", track_visibility="always")
    health_condition_ids = fields.One2many('health.condition', 'employee_id', string="Health Condition")
    employee_dependent_ids = fields.One2many('hr.employee.dependents', 'employee_id', string="Employee Dependents")
