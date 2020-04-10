# -*- coding: utf-8 -*- Part of Odoo. See LICENSE file for full copyright and
# licensing details.

from datetime import datetime
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons import decimal_precision as dp


class CollectionOrder(models.Model):
    _name = "collection.order"
    _inherit = ['mail.thread']
    _description = "Collection Order"
    _order = 'date_order desc, id desc'

    @api.depends('collection_line_ids.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.collection_line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    def _get_purchase(self):
        for order in self:
            search_purchase = self.env['purchase.order'].search(
                [('collection_id', '=', order.id)])
            if search_purchase:
                order.update({'purchase_count': len(
                    [i.id for i in search_purchase])})

    def _get_sale(self):
        for order in self:
            search_sale = self.env['sale.order'].search(
                [('collection_id', '=', order.id)])
            if search_sale:
                order.update({'sale_count': len([i.id for i in search_sale])})

    def _get_waybill(self):
        for order in self:
            search_waybill = self.env['bill.lading'].search(
                [('collection_id', '=', order.id)])
            if search_waybill:
                order.update(
                    {'waybill_count': len([i.id for i in search_waybill])})

    @api.multi
    def action_co_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'ballester_collection', 'email_template_edi_collection')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'collection.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={
                       'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one(
        'res.partner', 'Vendor', domain="[('supplier','=', True)]", required=True)
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address', readonly=True, required=True, states={
                                         'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Invoice address for current sales order.")
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', readonly=True, required=True, states={
                                          'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current sales order.")
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={
                                 'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
    partner_ref = fields.Char(string='Vendor Reference', copy=False)
    state = fields.Selection([
        ('draft', 'New'),
        ('in_process', 'In Process'),
        ('picked_up', 'Picked Up'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    collection_line_ids = fields.One2many('collection.order.line', 'order_id', states={
                                          'cancel': [('readonly', True)]}, copy=True, auto_join=True)
    note = fields.Text('Terms and conditions')
    user_id = fields.Many2one('res.users', string='User By', index=True,
                              track_visibility='onchange', default=lambda self: self.env.user)
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('collection.order'))
    source_location_id = fields.Many2one('stock.location', 'Source Location')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    destination_location_id = fields.Many2one(
        'stock.location', 'Destination Location')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True,
                                     readonly=True, compute='_amount_all', track_visibility='onchange')
    amount_tax = fields.Monetary(
        string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(
        string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    purchase_type = fields.Selection([('minor', 'Minor Purchases'), (
        'complex', 'Complex Purchases'), ], 'Type of Purchase')
    sales_type = fields.Selection(
        [('new', 'New'), ('recycled', 'Recycled'), ('sddr', 'SDDR'), ('waste', 'Waste'), ], 'Type of Sale')
    purchase_count = fields.Integer(
        'Purchase Count', compute='_get_purchase', readonly=True)
    sale_count = fields.Integer(
        'Sale Count', compute='_get_sale', readonly=True)
    waybill_count = fields.Integer(
        'Waybill', compute='_get_waybill', readonly=True)
    collection_type = fields.Selection(
        [('purchase', 'Purchases'), ('sale', 'Sales')], required=True)

    @api.multi
    def action_process(self):
        return self.write({'state': 'in_process'})

    @api.multi
    def print_quotation(self):
        return self.env.ref('ballester_collection.collection_order_report').report_action(self)

    @api.multi
    def action_pickup(self):
        if self.collection_type == 'purchase':
            purchase_vals = {'partner_id': self.partner_id.id,
                             'company_id': self.company_id.id,
                             'collection_id': self.id,
                             'collection_line_ids': [(6, 0, [i.id for i in self.collection_line_ids])],
                             'purchase_type': self.purchase_type,
			      'transportation_name': self.vehicle_id.id ,
			     'source_location_id': self.source_location_id.id,
			     'destination_location_id': self.destination_location_id.id,
                             }
            create_purchase = self.env['purchase.order'].create(purchase_vals)
            create_purchase.write(
                {'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT), })
            self.write({'state': 'picked_up'})
            action = self.env.ref('purchase.purchase_rfq').read()[0]
            action['views'] = [
                (self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = create_purchase.id
        elif self.collection_type == 'sale':
            sale_vals = {'partner_id': self.partner_id.id,
                         'company_id': self.company_id.id,
                         'collection_id': self.id,
                         'collection_line_ids': [(6, 0, [i.id for i in self.collection_line_ids])],
                         'sales_type': self.sales_type,
		         'transportation_name': self.vehicle_id.id ,
			'source_location_id': self.source_location_id.id,
			 'destination_location_id': self.destination_location_id.id,
                          }
            create_sale = self.env['sale.order'].create(sale_vals)
            create_sale.write({'date_planned': datetime.today(
            ).strftime(DEFAULT_SERVER_DATETIME_FORMAT), })
            self.write({'state': 'picked_up'})
            action = self.env.ref('sale.action_quotations').read()[0]
            action['views'] = [
                (self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = create_sale.id
        return action

    @api.multi
    def action_view_purchase(self):
        purchase_ids = self.env['purchase.order'].search(
            [('collection_id', '=', self.id)])
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        if purchase_ids:
            action['views'] = [
                (self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = purchase_ids[0].id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_waybill(self):
        waybill_ids = self.env['bill.lading'].search(
            [('collection_id', '=', self.id)])
        action = self.env.ref(
            'ballester_collection.action_bill_of_lading_general').read()[0]
        if waybill_ids:
            action['views'] = [
                (self.env.ref('ballester_collection.view_bill_of_lading_form').id, 'form')]
            action['res_id'] = waybill_ids[0].id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_sale(self):
        purchase_ids = self.env['sale.order'].search(
            [('collection_id', '=', self.id)])
        action = self.env.ref('sale.action_quotations').read()[0]
        if purchase_ids:
            action['views'] = [
                (self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = purchase_ids[0].id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
            })
            return
        partner_obj = self.env['res.partner']
        search_productor_partner_ids = partner_obj.search([('type', '=', 'center'), (
            'center_type', '=', 'producer'), ('parent_id', '=', self.partner_id and self.partner_id.id or False)])
        if not search_productor_partner_ids:
            raise Warning(
                _('There is no Producer Center Defined for this Vendor'))
        values = {
            'partner_invoice_id': self.partner_id and self.partner_id.id,
            'partner_shipping_id': search_productor_partner_ids and search_productor_partner_ids[0].id,
            'user_id': self.partner_id.user_id.id or self.env.uid
        }
        self.update(values)


class CollectionOrderLine(models.Model):
    _name = 'collection.order.line'
    _description = 'Collection Order Line'
    _order = 'order_id'

    @api.multi
    @api.depends('product_id', 'collection_id')
    def name_get(self):
        result = []
        for line in self:
            name = line.order_id.name + ' / ' + line.product_id.name
            result.append((line.id, name))
        return result



    @api.depends('product_uom_qty', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - 0.0 / 100.0)
            taxes = line.tax_id.compute_all(
                price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    order_id = fields.Many2one('collection.order', string='Order Reference',
                               required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Text(string='Description', required=True)
    purchase_id = fields.Many2one('purchase.order', 'Purchases')
    sale_id = fields.Many2one('sale.order', 'Sales')
    sequence = fields.Integer(string='Sequence', default=10)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision(
        'Product Price'), default=0.0)

    price_subtotal = fields.Monetary(
        compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount',
                             string='Taxes', readonly=True, store=True)
    price_total = fields.Monetary(
        compute='_compute_amount', string='Total', readonly=True, store=True)

    price_reduce = fields.Float(compute='_get_price_reduce', string='Price Reduce',
                                digits=dp.get_precision('Product Price'), readonly=True, store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=[
                              '|', ('active', '=', False), ('active', '=', True)])
    price_reduce_taxinc = fields.Monetary(
        compute='_get_price_reduce_tax', string='Price Reduce Tax inc', readonly=True, store=True)
    price_reduce_taxexcl = fields.Monetary(
        compute='_get_price_reduce_notax', string='Price Reduce Tax excl', readonly=True, store=True)
    product_id = fields.Many2one('product.template', string='Product', domain=[(
        'sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision(
        'Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one(
        'product.uom', string='Unit of Measure', required=True)
    # Non-stored related field to allow portal user to see the image of the
    # product he has ordered
    product_image = fields.Binary(
        'Product Image', related="product_id.image", store=False)
    salesman_id = fields.Many2one(
        related='order_id.user_id', store=True, string='Salesperson', readonly=True)
    company_id = fields.Many2one(
        related='order_id.company_id', string='Company', store=True, readonly=True)
    currency_id = fields.Many2one(
        related='order_id.currency_id', store=True, string='Currency', readonly=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('in_process', 'In Process'),
        ('picked_up', 'Picked Up'),
        ('cancel', 'Cancelled'),
    ], related='order_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide
        # default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [
            ('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            self.taxes_id = self.product_id.supplier_taxes_id.filtered(
                lambda r: r.company_id.id == company_id)
        else:
            self.taxes_id = self.product_id.supplier_taxes_id

        return result
