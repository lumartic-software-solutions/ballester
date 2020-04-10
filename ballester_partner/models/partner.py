from odoo import api, fields, models, _
# coding=utf-8


class Partner(models.Model):
    """Partner"""
    _inherit = "res.partner"

    is_vendor_service = fields.Boolean(string="Is a Vendor Service")
    fax = fields.Char('Fax')
