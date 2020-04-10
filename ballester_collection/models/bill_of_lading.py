from odoo import api, fields, models, _


class BillOfLading(models.Model):
    _name = "bill.lading"

    name = fields.Char(string='Consignment Note Number', required=True,
                       copy=False, readonly=True, default=lambda self: _('New'))
    origin_id = fields.Many2one('res.partner', 'Origin', required=True)
    origin_tags = fields.Many2many(
        'bill.lading.tags', 'origin_rel_tags', string="Origin Tags")
    origin_contact_id = fields.Many2one(
        'res.partner', 'Origin Contact', )
    carrier_id = fields.Many2one(
        'res.partner', 'Effective Carrier')
    carrier_tags = fields.Many2many(
        'bill.lading.tags', 'carrier_rel_tags', string="Effective Carrier Tags")
    carrier_contact_id = fields.Many2one(
        'res.partner', 'Carrier Contact')
    destination_id = fields.Many2one(
        'res.partner', 'Destination', required=True)
    destination_tags = fields.Many2many(
        'bill.lading.tags', 'destination_rel_tags', string="Destination Tags")
    destination_contact_id = fields.Many2one(
        'res.partner', 'Destination Contact')
    loading_date = fields.Date('Loading Date', required=True)
    download_date = fields.Date('Download Date', required=True)
    obervations = fields.Text('Observations')
    collection_id = fields.Many2one('collection.order', "Collection Order")
    sale_id = fields.Many2one('sale.order', "Sale Order")
    purchase_id = fields.Many2one('purchase.order', "Purchase Order")

    @api.model
    def default_get(self, default_fields):
        res = super(BillOfLading, self).default_get(default_fields)
        ctx = dict(self._context)
        if ctx.get('active_model') == 'sale.order':
            sale = self.env['sale.order'].browse(ctx.get('active_id'))
            
            res.update({
                        'origin_id': sale.company_id.partner_id and sale.company_id.partner_id.id,
			'sale_id':sale.id,
			'loading_date':sale.date_order,
			'download_date': sale.date_order,
			'destination_id' : sale.partner_id and  sale.partner_id.id,
			})
        else:
            collection = self.env['collection.order'].browse(ctx.get('active_id'))
            res.update({'collection_id': ctx.get('active_id'),
                        'origin_id': collection.partner_id and collection.partner_id.id,
			'loading_date':collection.date_order,
			'download_date': collection.date_order,
			'destination_id' : collection.company_id.partner_id and  collection.company_id.partner_id.id,
			})
        return res


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'bill.lading') or _('New')
        result = super(BillOfLading, self).create(vals)
        return result

    @api.multi
    def print_waybill(self):
        return self.env.ref('ballester_collection.bill_of_lading').report_action(self)

    @api.multi
    @api.onchange('origin_contact_id')
    def origin_contact_id_change(self):
        if self.origin_id.child_ids:
            domain = {'origin_contact_id': [('id', '=', [i.id for i in self.origin_id.child_ids])] }
            result = {'domain': domain}
            
            return result  


    @api.multi
    @api.onchange('destination_contact_id')
    def destination_contact_id_change(self):
        if self.destination_id.child_ids:
            domain = {'destination_contact_id': [('id', '=', [i.id for i in self.destination_id.child_ids])] }
            result = {'domain': domain}
            
            return result               
                
         


class BillOfLadingTags(models.Model):
    _name = "bill.lading.tags"

    name = fields.Char(string='Name', required=True)
