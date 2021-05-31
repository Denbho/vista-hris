from odoo import fields, models, api


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    office_id = fields.Many2one('hr.office.location', string="Office", track_visibility="always")
    work_location = fields.Char(string="Work Location", track_visibility="always", store=True,
                                compute="_get_office_location")

    @api.depends('office_id')
    def _get_office_location(self):
        for r in self:
            location = ""
            if r.office_id:
                office = r.office_id
                location += f"{office.street} "
                if office.street2:
                    location += f"{office.street2}"
                if office.barangay_id:
                    if location != "":
                        location += ", "
                    location += f"{office.barangay_id.name}"
                if office.city_id:
                    if location != "":
                        location += ", "
                    location += f"{office.city_id.name}"
                if office.province_id:
                    if location != "":
                        location += ", "
                    location += f"{office.province_id.name}"
                if office.state_id:
                    if location != "":
                        location += ", "
                    location += f"{office.state_id.name}"
                if office.zip:
                    if location != "":
                        location += ", "
                    location += f"{office.zip}"
                if office.country_id:
                    if location != "":
                        location += ", "
                    location += f"{office.country_id.name}"
            r.work_location = location


class HROfficeLocation(models.Model):
    _name = 'hr.office.location'
    _description = 'Office Location'

    name = fields.Char(string="Name", required=True)
    continent_id = fields.Many2one('res.continent', string="Continent")
    continent_region_id = fields.Many2one('res.continent.region')
    country_id = fields.Many2one('res.country', string="Country")
    island_group_id = fields.Many2one('res.island.group', string="Island Group")
    state_id = fields.Many2one('res.country.state', string="Region")
    province_id = fields.Many2one('res.country.province', string="Province")
    city_id = fields.Many2one('res.country.city', string="City Name")
    barangay_id = fields.Many2one('res.barangay', string="Barangay")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    zip = fields.Char(string="Zip")

    @api.model
    def create(self, vals):
        barangay = list()
        if vals.get('barangay_id'):
            barangay = self.env['res.barangay'].browse(vals.get('barangay_id'))
        elif vals.get('zip'):
            barangay = self.env['res.barangay'].search([('zip_code', '=', vals.get('zip'))], limit=2)
        if barangay and barangay[:1]:
            data = barangay[:1]
            vals['zip'] = data.zip_code
            vals['barangay_id'] = len(barangay) == 1 and data.id or False
            vals['city_id'] = data.city_id.id
            vals['province_id'] = data.province_id.id
            vals['state_id'] = data.state_id.id
            vals['island_group_id'] = data.island_group_id.id
            vals['country_id'] = data.country_id.id
            vals['continent_region_id'] = data.continent_region_id.id
            vals['continent_id'] = data.continent_id.id
        return super(HROfficeLocation, self).create(vals)

    def write(self, vals):
        barangay = list()
        if vals.get('barangay_id'):
            barangay = self.env['res.barangay'].browse(vals.get('barangay_id'))
        elif vals.get('zip'):
            barangay = self.env['res.barangay'].search([('zip_code', '=', vals.get('zip'))], limit=2)
        if barangay and barangay[:1]:
            data = barangay
            vals['zip'] = data.zip_code
            vals['barangay_id'] = len(barangay) == 1 and data.id or False
            vals['city_id'] = data.city_id.id
            vals['province_id'] = data.province_id.id
            vals['state_id'] = data.state_id.id
            vals['island_group_id'] = data.island_group_id.id
            vals['country_id'] = data.country_id.id
            vals['continent_region_id'] = data.continent_region_id.id
            vals['continent_id'] = data.continent_id.id
        return super(HROfficeLocation, self).write(vals)

    @api.onchange('barangay_id')
    def onchange_barangay(self):
        if self.barangay_id:
            data = self.barangay_id
            self.zip = data.zip_code or False
            self.city_id = data.city_id and data.city_id.id or False

    @api.onchange('city_id')
    def onchange_city(self):
        if self.city_id:
            data = self.city_id
            self.province_id = data.province_id and data.province_id.id or False

    @api.onchange('province_id')
    def onchange_province(self):
        if self.province_id:
            data = self.province_id
            self.state_id = data.state_id and data.state_id.id

    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            data = self.state_id
            self.island_group_id = data.island_group_id and data.island_group_id.id or False
            self.country_id = data.country_id.id

    @api.onchange('island_group_id')
    def onchange_island_group(self):
        if self.island_group_id:
            data = self.island_group_id
            self.country_id = data.country_id.id or False

    @api.onchange('country_id')
    def onchange_country(self):
        if self.country_id:
            data = self.country_id
            self.continent_region_id = data.continent_region_id and data.continent_region_id.id or False

    @api.onchange('continent_region_id')
    def onchange_continent_region_i(self):
        if self.continent_region_id:
            data = self.continent_region_id
            self.continent_id = data.continent_id and data.continent_id.id or False

