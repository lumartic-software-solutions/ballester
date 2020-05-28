# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Product.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def create(self, vals):
        if vals.get('origin'):
            sale_brw = self.env['sale.order'].search([('name','=' , vals.get('origin'))])
            if sale_brw:
                if sale_brw.source_location_id:
                    vals['location_id'] = sale_brw.source_location_id.id
                if sale_brw.destination_location_id:
                    vals['location_dest_id'] = sale_brw.destination_location_id.id
        result = super(Picking, self).create(vals)
        return result


    # @api.multi
    # def action_assign(self):
    #     """ Check availability of picking moves.
    #     This has the effect of changing the state and reserve quants on available moves, and may
    #     also impact the state of the picking as it is computed based on move's states.
    #     @return: True
    #     """
    #     self.filtered(lambda picking: picking.state == 'draft').action_confirm()
    #     moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
    #     if not moves:
    #         raise UserError(_('Nothing to check the availability for.'))
    #     moves._action_assign()
    #     for move in moves:
    #         if move.sale_line_id:
    #             if move.sale_line_id.lot_ids:
    #                 for lot in move.sale_line_id.lot_ids:
    #                     move_lines = {
	# 	                    'lot_id': lot.id or False,
	# 	                    'move_id':move.id,
	# 	                    'date': move.date,
	# 	                    'location_dest_id': move.location_dest_id.id,
	# 	                    'location_id':move.location_id.id,
	# 	                    'product_uom_id': move.product_uom.id ,
	# 	                    'ordered_qty':1.0,
	# 	                    'product_id':move.product_id.id,
	# 	                }
    #                     move_id =self.env['stock.move.line'].create(move_lines)
    #     return True

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self, vals):
        print("--------@@@@@----------------", vals)
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



