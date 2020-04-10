# -*- coding: utf-8 -*-
# Odoo, Open Source  Stock Transport Management.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class VehicleStatus(models.Model):
    _name = 'vehicle.status'

    name = fields.Char(string="Vehicle Name", required=True)
    transport_date = fields.Date(string="Transportation Date")
    no_parcels = fields.Char(string="No of Parcels")
    order = fields.Char(string='Order Reference')
    sale_id = fields.Many2one('sale.order',string='Sale Order')
    purchase_id = fields.Many2one('purchase.order',string='Purchase Order')
    delivery_order = fields.Char(string="Delivery Order")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('start', 'Start'),
        ('waiting', 'Waiting'),
        ('cancel', 'Cancel'),
        ('done', 'Done'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    def start_action(self):
        vehicle = self.env['fleet.vehicle'].search([('name', '=', self.name)])
        vals = {'active_available': False}
        vehicle.write(vals)
        self.write({'state': 'start'})

    def action_cancel(self):
        self.write({'state': 'cancel'})
        vehicle = self.env['fleet.vehicle'].search([('name', '=', self.name)])
        vals = {'active_available': True}
        vehicle.write(vals)

    def action_done(self):
        self.write({'state': 'done'})
        vehicle = self.env['fleet.vehicle'].search([('name', '=', self.name)])
        vals = {'active_available': True}
        vehicle.write(vals)

    def action_waiting(self):
        vehicle = self.env['fleet.vehicle'].search([('name', '=', self.name)])
        vals = {'active_available': False}
        vehicle.write(vals)
        self.write({'state': 'waiting'})

    def action_reshedule(self):
        self.write({'state': 'draft'})
