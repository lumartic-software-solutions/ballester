# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    collection_id = fields.Many2one('collection.order', 'Collection Order')
    collection_line_ids = fields.One2many('collection.order.line', 'sale_id', 'Order Lines')
    source_location_id = fields.Many2one('stock.location', 'Source Location')
    destination_location_id = fields.Many2one(
        'stock.location', 'Destination Location' )
    waybill_count = fields.Integer(
        'Waybill', compute='_get_waybill', readonly=True)

    def _get_waybill(self):
        for order in self:
            search_waybill = self.env['bill.lading'].search(
                [('sale_id', '=', order.id)])
            if search_waybill:
                order.update(
                    {'waybill_count': len([i.id for i in search_waybill])})

    @api.onchange('source_location_id')
    def onchange_source_location_id(self):
        if self.source_location_id:
            search_warehouse_ids = self.env['stock.warehouse'].search([('lot_stock_id','=', self.source_location_id.id)])
            if search_warehouse_ids:
                self.warehouse_id = search_warehouse_ids[0].id
          
    @api.multi
    def action_view_waybill(self):
        waybill_ids = self.env['bill.lading'].search(
            [('sale_id', '=', self.id)])
        action = self.env.ref(
            'ballester_collection.action_bill_of_lading_general').read()[0]
        if waybill_ids:
            action['views'] = [
                (self.env.ref('ballester_collection.view_bill_of_lading_form').id, 'form')]
            action['res_id'] = waybill_ids[0].id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        
        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        result = {'domain': domain}
       
           

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        return result
