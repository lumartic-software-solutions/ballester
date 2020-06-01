# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Product.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def create(self, vals):
        if vals.get('origin'):
            sale_brw = self.env['sale.order'].search([('name', '=', vals.get('origin'))])
            if sale_brw:
                if sale_brw.source_location_id:
                    vals['location_id'] = sale_brw.source_location_id.id
                if sale_brw.destination_location_id:
                    vals['location_dest_id'] = sale_brw.destination_location_id.id
        result = super(Picking, self).create(vals)
        return result

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self, vals):
        if vals.get('origin'):
            sale_brw = self.env['sale.order'].search([('name', '=', vals.get('origin'))])
            if sale_brw:
                if sale_brw.source_location_id:
                    vals['location_id'] = sale_brw.source_location_id.id
                if sale_brw.destination_location_id:
                    vals['location_dest_id'] = sale_brw.destination_location_id.id
        res = super(StockMove, self).create(vals)
        return res


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        lot_ids =[]
        lot_purchase_ids = []
        ctx = self._context
        if ctx.get('sale'):
            self.env.cr.execute('select lot_id from lot_sale_line_rel')
            res = self.env.cr.fetchall()
            if res:
                lot_ids = [lot[0] for lot in res]
                args += [('id','not in', lot_ids)]
        if ctx.get('purchase'):
            self.env.cr.execute('select lot_id from lot_purchase_line_rel')
            res = self.env.cr.fetchall()
            if res:
                lot_purchase_ids = [lot[0] for lot in res]
                args += [('id','not in', lot_purchase_ids)]
        recs = self.search(args, limit=limit)
        return recs.name_get()



