# -*- coding: utf-8 -*-
# Odoo, Open Source  Stock Transport Management.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class VehicleSaleOrder(models.Model):
    _inherit = 'stock.picking'

    transportation_name = fields.Char(string="Transportation Via", compute="get_transportation")
    no_parcels = fields.Integer(string="No Of Parcels")
    transportation_details = fields.One2many('vehicle.status', compute='fetch_details', string="Transportation Details")

    @api.multi
    def get_transportation(self):
        if self.sale_id :
            res = self.env['sale.order'].search([('name', '=', self.sale_id.name)])
            self.transportation_name = res.transportation_name.name
            order = self.env['vehicle.status'].search([('sale_id', '=', self.sale_id.id)])
        elif self.purchase_id :
            res = self.env['purchase.order'].search([('name', '=', self.purchase_id.name)])
            self.transportation_name = res.transportation_name.name
            order = self.env['vehicle.status'].search([('purchase_id', '=', self.purchase_id.name)])
        else:
            order = True
        if not order and self.transportation_name:
            vals = {'name': self.transportation_name,
                    'no_parcels': self.no_parcels,
                    'sale_id' : self.sale_id.id or False,
                    'purchase_id' : self.purchase_id.id  or False,
                    'order': self.sale_id.name or self.purchase_id.name or '' ,
                    'delivery_order': self.name,
                    'transport_date': self.scheduled_date,
                    }
            obj = self.env['vehicle.status'].create(vals)
            return obj

    @api.onchange('no_parcels')
    def get_parcel(self):
        if self.sale_id :
            order = self.env['vehicle.status'].search([('sale_id', '=', self.sale_id.id)])
        elif self.purchase_id :
            order = self.env['vehicle.status'].search([('purchase_id', '=', self.purchase_id.id)])
        else:
            order = False
        if order :
            vals = {'no_parcels': self.no_parcels}
            order.write(vals)
            

    @api.multi
    def fetch_details(self):
        if self.sale_id :
            order = self.env['vehicle.status'].search([('sale_id', '=', self.sale_id.id)])
        elif self.purchase_id :
            order = self.env['vehicle.status'].search([('purchase_id', '=', self.purchase_id.id)])
        else:
            order = False
        if order :
            self.transportation_details = order
