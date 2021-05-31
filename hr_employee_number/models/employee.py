from odoo import fields, models, api, _


class HREmployee(models.Model):
    _inherit = 'hr.employee'
    _sql_constraints = [('employee_number', 'unique(employee_number)',
                         'The "Employee Number" field  must have unique value!')]

    employee_number = fields.Char(string="Employee Number", track_visibility="always", copy=False)

    @api.model
    def create(self, vals):
        if not vals.get('employee_number'):
            vals['employee_number'] = self.env['ir.sequence'].get('hr.employee.id.number')
        return super(HREmployee, self).create(vals)

