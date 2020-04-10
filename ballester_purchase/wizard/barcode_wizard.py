# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class BarcodeWizard(models.TransientModel):
    _name = 'barcode.wizard'
    _description = 'Barcode Wizard'

    name = fields.Text('Lot/Barcode')

    @api.model
    def default_get(self, default_fields):
        res = super(BarcodeWizard, self).default_get(default_fields)
         
        return res

    
    @api.multi
    def barcode_button(self):
        lot_obj = self.env['stock.production.lot']
        ctx = self._context
        line_id = ctx.get('active_id')
        purchase_order_line = self.env['purchase.order.line'].browse(line_id)
        if purchase_order_line.lot_ids:
            raise ValidationError("Ya has agregado el código de barras")
        values = self.name
        if values:
            spilt_value = values.split('\n')
            barcode_value = spilt_value
            if barcode_value:
                search_lot_ids = lot_obj.search([('name','in', barcode_value)])
                if search_lot_ids:
                    if purchase_order_line:
                        if purchase_order_line.product_qty > len(search_lot_ids):
                            raise ValidationError("No puede agregar menos código de barras que la cantidad del producto")
                        elif  purchase_order_line.product_qty < len(search_lot_ids):   
                            raise ValidationError("No puede agregar más código de barras que la cantidad de producto")
                        purchase_order_line.write({'lot_ids': [(6,0, [ i.id for i in search_lot_ids ])]})
        return True


    

