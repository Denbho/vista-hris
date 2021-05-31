from odoo import fields, models, api, _
from datetime import date, datetime
from odoo.exceptions import ValidationError
import tempfile
import binascii
import xlrd


class ResumeLineType(models.Model):
    _inherit = 'hr.resume.line.type'

    display_type = fields.Selection([('classic', 'Classic'), ('course', 'Course'), ('certification', 'Certification')], string="Display Type", default='classic')


class ResumeImport(models.Model):
    _name = 'hr.resume.import'
    _inherit = ["mail.thread", "mail.activity.mixin", "resource.mixin"]
    _description = "Resume Line Import"
    _rec_name = 'date'

    date = fields.Date(string="Import Date", required=True, track_visibility="always",
                       default=fields.Date.context_today)
    file_to_upload = fields.Binary('File', track_visibility="always")
    import_data_ids = fields.One2many("hr.resume.line.import", 'resume_import_id', string="Import Data")
    import_done = fields.Boolean(string="Import Done")
    data_validated = fields.Boolean(string="Data Validated")

    def import_validated_data(self):
        if len(self.import_data_ids) >= 1:
            for r in self.import_data_ids:
                data = self.env['hr.resume.line'].create(
                    {
                        'employee_id': r.employee_id.id,
                        'name': r.name,
                        'description': r.description,
                        'line_type_id': r.line_type_id.id,
                        'display_type': r.display_type,
                        'date_start': r.date_start,
                        'date_end': r.date_end
                    }
                )
            self.write({'import_done': True})

    def import_xls_file(self):
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file_to_upload))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
        except:
            raise Warning(_('Invalid Excel File!!'))
        data = list()
        emp = self.env['hr.employee']
        line_type = self.env['hr.resume.line.type']
        for row_no in range(sheet.nrows):
            val = {}
            if row_no <= 0:
                fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = list(
                    map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                        sheet.row(row_no)))
                # raise ValidationError(_(f'{line}'))
                # if line[0] == '' or line[1] == '' or line[3] == '' or line[4] == '':
                start_date = str(xlrd.xldate.xldate_as_datetime(int(float(line[4])), workbook.datemode))
                end_date = line[5] != '' and str(
                    xlrd.xldate.xldate_as_datetime(int(float(line[5])), workbook.datemode)) or False
                employee = emp.sudo().search([('employee_number', '=', line[0])], limit=1)
                if not employee[:1]:
                    raise ValidationError(_(f'There is no employee record matched with the {line[0]} employee ID number.'))
                line_type_rec = line_type.sudo().search([('name', '=', line[3])], limit=1)
                if not line_type_rec[:1]:
                    raise ValidationError(_(f'Display Type {line[3]} not yet configured in the system.'))
                values = {
                    'employee_number': line[0],
                    'employee_id': employee.id,
                    'name': line[1],
                    'description': line[2],
                    'line_type_id': line_type_rec.id,
                    'display_type': line_type_rec.display_type,
                    'date_start': start_date,
                    'date_end': end_date
                }
                data.append([0, 0, values])
                # else:
                #     raise ValidationError(_(
                #         f' {line[0]}, {line[1]}, {line[3]}, {line[4]}\nPlease make sure to define the following in their corresponding columns and Sequence: \n\t1. Employee Number, \n\t2. Item Name, \n\t3. Item Type, \n\t4. Date Start'))
        self.write({'import_data_ids': data, 'data_validated': True})
        return True

# employee_number, name, description, item_type, date_start, date_end


class ResumeLineImport(models.Model):
    _name = 'hr.resume.line.import'
    _inherit = 'hr.resume.line'

    resume_import_id = fields.Many2one('hr.resume.import', string="Import Origin")
    employee_number = fields.Char(string="Employee ID")
    remarks = fields.Text(string="Import Remarks")


class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    @api.onchange('line_type_id')
    def onchange_line_type_id(self):
        if self.line_type_id:
            self.display_type = self.line_type_id.display_type

