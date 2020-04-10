# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _


class AccountInvocie(models.Model):
    _inherit = "account.invoice"

    collection_id = fields.Many2one('collection.order', 'Collection Order')
    source_location_id = fields.Many2one('stock.location', 'Source Location',related='collection_id.source_location_id')
    destination_location_id = fields.Many2one(
        'stock.location', 'Destination Location',related='collection_id.destination_location_id')
    

    @api.model
    def default_get(self, default_fields):
        res = super(AccountInvocie, self).default_get(default_fields)
        ctx = dict(self._context)
        if ctx.get('active_model') == 'purchase.order':
            purchase_ids = self.env['purchase.order'].browse(ctx.get('active_id'))
            res.update({'collection_id': purchase_ids[0].collection_id.id})
        return res
    
