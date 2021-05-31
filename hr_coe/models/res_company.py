# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
	_inherit = 'res.company'

	old_name = fields.Char('Old Company Name')