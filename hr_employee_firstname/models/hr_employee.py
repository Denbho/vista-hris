# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

UPDATE_PARTNER_FIELDS = ["firstname", "lastname", "user_id", "address_home_id"]


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def _get_name(self, lastname, firstname, middle_name, suffix_name):
        return self.env["res.partner"]._get_computed_name(lastname, firstname, middle_name, suffix_name)

    @api.onchange("firstname", "lastname", "middle_name", "suffix_name")
    def _onchange_firstname_lastname(self):
        if self.firstname or self.lastname:
            self.name = self._get_name(self.lastname, self.firstname, self.middle_name, self.suffix_name)

    firstname = fields.Char(string="First Name", tracking=True)
    lastname = fields.Char(string="Last Name", tracking=True)
    middle_name = fields.Char(string="Middle Name", tracking=True)
    nick_name = fields.Char(string="Nick Name (AKA)", tracking=True)
    suffix_name = fields.Char(string="Suffix Name", tracking=True)
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widowed'),
        ('divorced', 'Divorced'),
        ('separated', 'Separated'),
        ('annulled', 'Annulled')
    ], string='Marital Status', tracking=True)

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.firstname = self.user_id.firstname
            self.lastname = self.user_id.lastname
            self.middle_name = self.user_id.middle_name
            self.suffix_name = self.user_id.suffix_name

    @api.model
    def create(self, vals):
        if vals.get("firstname") or vals.get("lastname"):
            vals["name"] = self._get_name(vals.get("lastname"), vals.get("firstname"), vals.get('middle_name'), vals.get('suffix_name'))
        elif vals.get("name"):
            vals["lastname"] = self.split_name(vals["name"])["lastname"]
            vals["firstname"] = self.split_name(vals["name"])["firstname"]
        else:
            raise ValidationError(_("No name set."))
        res = super().create(vals)
        res._update_partner_firstname()
        return res

    def write(self, vals):
        if "firstname" in vals or "lastname" in vals:
            if "lastname" in vals:
                lastname = vals.get("lastname")
            else:
                lastname = self.lastname
            if "firstname" in vals:
                firstname = vals.get("firstname")
            else:
                firstname = self.firstname
            vals["name"] = self._get_name(lastname, firstname, vals.get('middle_name'), vals.get('suffix_name'))
        elif vals.get("name"):
            vals["lastname"] = self.split_name(vals["name"])["lastname"]
            vals["firstname"] = self.split_name(vals["name"])["firstname"]
        res = super().write(vals)
        if set(vals).intersection(UPDATE_PARTNER_FIELDS):
            self._update_partner_firstname()
        return res

    @api.model
    def split_name(self, name):
        clean_name = " ".join(name.split(None)) if name else name
        return self.env["res.partner"]._get_inverse_name(clean_name)

    def _inverse_name(self):
        """Try to revert the effect of :meth:`._compute_name`."""
        for record in self:
            parts = self.env["res.partner"]._get_inverse_name(record.name)
            record.lastname = parts["lastname"]
            record.firstname = parts["firstname"]

    @api.model
    def _install_employee_firstname(self):
        """Save names correctly in the database.

        Before installing the module, field ``name`` contains all full names.
        When installing it, this method parses those names and saves them
        correctly into the database. This can be called later too if needed.
        """
        # Find records with empty firstname and lastname
        records = self.search([("firstname", "=", False), ("lastname", "=", False)])

        # Force calculations there
        records._inverse_name()
        _logger.info("%d employees updated installing module.", len(records))

    def _update_partner_firstname(self):
        for employee in self:
            partners = employee.mapped("user_id.partner_id")
            partners |= employee.mapped("address_home_id")
            partners.write(
                {"firstname": employee.firstname, "lastname": employee.lastname, 'middle_name': employee.middle_name, 'suffix_name': employee.suffix_name}
            )

    @api.constrains("firstname", "lastname")
    def _check_name(self):
        """Ensure at least one name is set."""
        for record in self:
            if not (record.firstname or record.lastname):
                raise ValidationError(_("No name set."))
