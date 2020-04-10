# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Product.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sales_type = fields.Selection(
        [('new', 'New'), ('recycled', 'Recycled'), ('sddr', 'SDDR'), ('waste', 'Waste'), ], 'Type of Sale')


# add multi barcode in sale order line
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_ids = fields.Many2many(
        'stock.production.lot', 'lot_sale_line_rel', 'lot_id', 'sale_line_id', 'Barcode')

    barcode_number = fields.Text('Lot/Barcode')

    @api.onchange('lot_ids')
    def onchange_lot_ids(self):
        if self.lot_ids:
            if len(self.lot_ids) > self.product_uom_qty:
                raise ValidationError(
                    "No puede agregar más código de barras que la cantidad de producto")

    
    @api.model
    def create(self, vals):
        lot_obj = self.env['stock.production.lot']
        res = super(SaleOrderLine, self).create(vals)
        product_lot_ids = []
        if vals.get('barcode_number'):
            spilt_value = vals.get('barcode_number').split('\n')
            barcode_value = spilt_value
            if barcode_value:
                search_lot_ids = lot_obj.search([('name','in', barcode_value)])
                if search_lot_ids:
                    if res.product_uom_qty > len(search_lot_ids):
                        raise UserError(_("la cantidad del producto de '%s' no puede ser más que el código de barras")%( res.product_id.name))
                    elif  res.product_uom_qty < len(search_lot_ids):   
                        raise UserError(_("la cantidad del producto de '%s' no puede ser inferior al código de barras")%( res.product_id.name))
                    res.lot_ids = [(6,0, [ i.id for i in search_lot_ids ])]
        if res.product_id and res.product_uom_qty and res.order_id.source_location_id:
            quant_search = self.env['stock.quant'].search([('product_id','=',res.product_id.id ),('location_id','=',res.order_id.source_location_id.id)])
            if quant_search:
                lot_ids = []
                if len(quant_search) == res.product_uom_qty:
                    for i in quant_search:
                        lot_ids.append(i.lot_id.id)
                    product_lot_ids =  [(6,0, lot_ids)]
                    res.lot_ids = product_lot_ids
        if not vals.get('barcode_number') and not vals.get('is_delivery') :
            if not product_lot_ids:
                if vals.get('product_id'):
                    product_search = self.env['product.product'].browse(vals.get('product_id'))
                    if product_search:
                        if product_search.type == 'product':
                            raise UserError(_("por favor agregue código de barras en este producto '%s' ")%( res.product_id.name))
        return res

    @api.multi
    def write(self, vals):
        lot_obj = self.env['stock.production.lot']
        if vals.get('barcode_number'):
            spilt_value = vals.get('barcode_number').split('\n')
            barcode_value = spilt_value
            if barcode_value:
                search_lot_ids = lot_obj.search([('name','in', barcode_value)])
                if search_lot_ids:
                    if self.product_uom_qty > len(search_lot_ids):
                        raise UserError(_("la cantidad del producto de '%s' no puede ser más que el código de barras")%( self.product_id.name))
                    elif  self.product_uom_qty < len(search_lot_ids):   
                        raise UserError(_("la cantidad del producto de '%s' no puede ser inferior al código de barras")%( self.product_id.name))
                    vals['lot_ids'] =  [(6,0, [ i.id for i in search_lot_ids ])]
        if self.barcode_number and not self.lot_ids:
            spilt_value = self.barcode_number.split('\n')
            barcode_value = spilt_value
            if barcode_value:
                search_lot_ids = lot_obj.search([('name','in', barcode_value)])
                if search_lot_ids:
                    if self.product_uom_qty > len(search_lot_ids):
                        raise UserError(_("la cantidad del producto de '%s' no puede ser más que el código de barras")%( self.product_id.name))
                    elif  self.product_uom_qty < len(search_lot_ids):   
                        raise UserError(_("la cantidad del producto de '%s' no puede ser inferior al código de barras")%( self.product_id.name))
                    vals['lot_ids'] =  [(6,0, [ i.id for i in search_lot_ids ])]
        res = super(SaleOrderLine, self).write(vals)
        return res



class StockProductionLotSalePurchase(models.Model):
    _inherit = 'stock.production.lot'

    api.multi
    def name_get(self):
        res = super(StockProductionLotSalePurchase, self).name_get()
        ctx = self._context
        sample_product_id = self.env.ref('ballester_screen.sample_product_id').id
        lot_ids = self.search([('product_id','=',sample_product_id)])
        data = []
        if ctx.get('product_id'):
            product_lot_search = self.search([('product_id','=', ctx.get('product_id'))])
            if product_lot_search:
                for i in product_lot_search:
                    data.append((i.id, i.name))
        if ctx.get('purchase'):
            if lot_ids:
                for i in lot_ids:
                    data.append((i.id, i.name))
        if data:
            return data
        else:
            return res


    @api.model
    def search_read(
        self, domain=None, fields=None, offset=0,
            limit=None, order=None):
        ctx = self._context
        if ctx.get('sale') or ctx.get('purchase'):
            sample_product_id = self.env.ref('ballester_screen.sample_product_id').id
            lots = self.search([('product_id','=',sample_product_id)])
            domain = ([('id', 'in', [i.id for i in lots])])
        return super(StockProductionLotSalePurchase, self).search_read(
          domain, fields, offset, limit, order)
    

class StockmoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model
    def create(self, vals):
        if vals.get('lot_id'):
            lot_ids =self.env['stock.production.lot'].browse(vals.get('lot_id'))
            if lot_ids:
                if lot_ids[0].product_id.id != vals.get('product_id'):
                    lot_ids[0].product_id = vals.get('product_id')
                vals['lot_name'] = lot_ids[0].name
        ml = super(StockmoveLine, self).create(vals)
        return ml

class Stockmove(models.Model):
    _inherit = 'stock.move'
    
    lot_ids = fields.Many2many(
        'stock.production.lot', 'lot_move_line_rel', 'lot_id', 'move_line_id', 'Barcode')

    
    # Automatically set lot number
    '''def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        self.ensure_one()
        # apply put away
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
        # pass values of product fields into lot
        if quantity:
            uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom, rounding_method='HALF-UP')
            uom_quantity_back_to_product_uom = self.product_uom._compute_quantity(uom_quantity, self.product_id.uom_id, rounding_method='HALF-UP')
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                vals = dict(vals, product_uom_qty=uom_quantity)
            else:
                vals = dict(vals, product_uom_qty=quantity, product_uom_id=self.product_id.uom_id.id)
        if reserved_quant:
            if self.product_id.tracking == 'serial' :
                product_vals= {'uncode': self.product_id.uncode or False,
                               'lercode_id' : self.product_id.lercode_id.id or False,
                               'admission_parameters': self.product_id.admission_parameters or False,
                               'treatement_operation_ids':  self.product_id.treatement_operation_ids.ids ,
                               'danger_char_ids': self.product_id.danger_char_ids.ids ,
                               'attribute_line_ids':self.product_id.product_tmpl_id.attribute_line_ids
                                }
                reserved_quant.lot_id.write(product_vals)
            vals = dict(
                vals,
                location_id=reserved_quant.location_id.id,
                lot_id=reserved_quant.lot_id.id or False,
                package_id=reserved_quant.package_id.id or False,
                owner_id =reserved_quant.owner_id.id or False,
            )
        return vals'''

