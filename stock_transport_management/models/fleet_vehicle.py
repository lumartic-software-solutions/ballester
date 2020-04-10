# -*- coding: utf-8 -*-
# Odoo, Open Source  Stock Transport Management.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields,api,_

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    mob_no = fields.Char(string="Mobile Number", required=True)
    vehicle_address = fields.Char(string="Address")
    vehicle_city = fields.Char(string='City')
    vehicle_zip = fields.Char(string='ZIP')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    
    @api.onchange('driver_id')
    def onchange_driver(self):
        if self.driver_id:
            if self.driver_id.mobile :
                self.mob_no=self.driver_id.mobile
            else:
                self.mob_no=''
