from odoo import fields, models, api
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    dyob = fields.Integer("Day of Birth", compute='_compute_yy_mm_of_birth', store=True, index=True,
                          help="The day of birth from the Date of Birth.")
    mob = fields.Integer(string='Month of Birth', compute='_compute_yy_mm_of_birth', store=True, index=True,
                         help="The month of birht from the Date of Birth.")
    yob = fields.Integer(string='Year of Birth', compute='_compute_yy_mm_of_birth', store=True, index=True,
                         help="The year of birth from the Date of Birth.")
    age = fields.Integer(string="Age", readonly=True)
    age_range_id = fields.Many2one('res.partner.age.range', string="Age Range")
    calendar_birthday = fields.Date(string="Calendar Birthday", readonly=True)

    def cron_calendar_birthday(self):
        current_year, current_month, current_day = self.split_date(date.today() - timedelta(days=1))
        employee = self.search([
            ('mob', '=', current_month),
            ('dyob', '=', current_day)
        ])
        for i in employee:
            i.write({
                'calendar_birthday': date.today() - relativedelta(days=1) + relativedelta(years=1)
            })

    def cron_compute_age(self):
        current_year, current_month, current_day = self.split_date(date.today())
        employee = self.search([
            ('mob', '=', current_month),
            ('dyob', '=', current_day)
        ])
        for i in employee:
            age = date.today().year - i.birthday.year
            age_range = self.env['res.partner.age.range'].search(
                [('range_from', '<=', age), ('range_to', '>=', age)], limit=1)
            i.write({
                'age': age,
                'age_range_id': age_range[:1] and age_range.id or False
            })

    @api.model
    def create(self, vals):
        if vals.get('birthday'):
            bday = datetime.strptime(vals.get('birthday'), "%Y-%m-%d")
            current_year, current_month, current_day = self.split_date(bday)
            age = date.today().year - bday.year
            age_range = self.env['res.partner.age.range'].search(
                [('range_from', '<=', age), ('range_to', '>=', age)], limit=1)
            vals.update({
                'age': age,
                'age_range_id': age_range[:1] and age_range.id or False
            })
            calendar_birthday = datetime.strptime(f"{date.today().year}-{current_month}-{current_day}", "%Y-%m-%d")
            if calendar_birthday <= datetime.now():
                calendar_birthday = calendar_birthday + relativedelta(years=1)
            vals['calendar_birthday'] = calendar_birthday
        return super(HREmployee, self).create(vals)

    def write(self, vals):
        if 'birthday' in vals and vals.get('birthday'):
            bday = datetime.strptime(vals.get('birthday'), "%Y-%m-%d")
            current_year, current_month, current_day = self.split_date(bday)
            age = date.today().year - bday.year
            age_range = self.env['res.partner.age.range'].search(
                [('range_from', '<=', age), ('range_to', '>=', age)], limit=1)
            vals.update({
                'age': age,
                'age_range_id': age_range[:1] and age_range.id or False
            })
            calendar_birthday = datetime.strptime(f"{date.today().year}-{current_month}-{current_day}", "%Y-%m-%d")
            if calendar_birthday <= datetime.now():
                calendar_birthday = calendar_birthday + relativedelta(years=1)
            vals['calendar_birthday'] = calendar_birthday
        return super(HREmployee, self).write(vals)

    @api.depends('birthday')
    def _compute_yy_mm_of_birth(self):
        for r in self:
            if not r.birthday:
                r.mob = False
                r.yob = False
                r.dyob = False
            else:
                year, month, day = self.split_date(fields.Date.from_string(r.birthday))
                r.dyob = day
                r.mob = month
                r.yob = year

    def split_date(self, date):
        """
        Method to split a date into year,month,day separatedly
        @param date date:
        """
        year = date.year
        month = date.month
        day = date.day
        return year, month, day
