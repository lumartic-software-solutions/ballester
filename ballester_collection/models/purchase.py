# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    collection_id = fields.Many2one('collection.order', 'Collection Order')
    collection_line_ids = fields.One2many('collection.order.line', 'purchase_id', 'Order Lines')
    source_location_id = fields.Many2one('stock.location', 'Source Location')
    
    destination_location_id = fields.Many2one(
        'stock.location', 'Destination Location' )
    waybill_count = fields.Integer(
        'Waybill', compute='_get_waybill', readonly=True)

    
    def _get_waybill(self):
        for order in self:
            search_waybill = self.env['bill.lading'].search(
                [('collection_id', '=', order.collection_id.id)])
            if search_waybill:
                order.update(
                    {'waybill_count': len([i.id for i in search_waybill])})


    @api.multi
    def action_view_waybill(self):
        waybill_ids = self.env['bill.lading'].search(
            [('collection_id', '=', self.collection_id.id)])
        action = self.env.ref(
            'ballester_collection.action_bill_of_lading_general').read()[0]
        if waybill_ids:
            action['views'] = [
                (self.env.ref('ballester_collection.view_bill_of_lading_form').id, 'form')]
            action['res_id'] = waybill_ids[0].id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
