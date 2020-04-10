# -*- coding: utf-8 -*-
# Odoo, Open Source  Stock Transport Management.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class VehicleCreation(models.Model):
    _name = 'sale.vehicle'

    name = fields.Char(string="Vehicle Name", required=True)
    driver_name = fields.Many2one('res.partner', string="Contact Name", required=True)
    vehicle_image = fields.Binary(string='Image', store=True, attachment=True)
    licence_plate = fields.Char(string="Licence Plate", required=True)
    mob_no = fields.Char(string="Mobile Number", required=True)
    vehicle_address = fields.Char(string="Address")
    vehicle_city = fields.Char(string='City')
    vehicle_zip = fields.Char(string='ZIP')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    active_available = fields.Boolean(string="Active", default=True)
