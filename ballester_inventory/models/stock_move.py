# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Inventory.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api,_
from datetime import datetime
from odoo.tools.float_utils import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"
    
    '''def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        self.ensure_one()
        # apply putaway
        location_dest_id = self.location_dest_id.get_putaway_strategy(self.product_id).id or self.location_dest_id.id
        vals = {
            'move_id': self.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'location_id': self.location_id.id,
            'location_dest_id': location_dest_id,
            'picking_id': self.picking_id.id,
        }
        # set lot name when product is set as unique serial number
        if self.product_id.tracking =='serial' 
            now = datetime.now()
            currentDay = now.strftime("%d")
            currentMonth = now.strftime("%m")
            currentYear = now.strftime("%y")
            if self.product_id.default_code :
                product_reference = self.product_id.default_code
            else :
                product_reference = str(000)
            get_product_code = product_reference[:3]
            sequence = self.env['ir.sequence'].next_by_code('stock.move.line') or _('New')
            lot_name = str(currentDay) + str(currentMonth) + str(currentYear)+  sequence
            vals.update({'lot_name' : lot_name,'qty_done':1})
        if quantity:
            uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom, rounding_method='HALF-UP')
            uom_quantity_back_to_product_uom = self.product_uom._compute_quantity(uom_quantity, self.product_id.uom_id, rounding_method='HALF-UP')
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                vals = dict(vals, product_uom_qty=uom_quantity)
            else:
                vals = dict(vals, product_uom_qty=quantity, product_uom_id=self.product_id.uom_id.id)
        if reserved_quant:
            vals = dict(
                vals,
                location_id=reserved_quant.location_id.id,
                lot_id=reserved_quant.lot_id.id or False,
                package_id=reserved_quant.package_id.id or False,
                owner_id =reserved_quant.owner_id.id or False,
            )
        return vals'''

    
