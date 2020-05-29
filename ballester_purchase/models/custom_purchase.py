# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Product.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, tools, api, _
from operator import itemgetter
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round, float_compare, float_is_zero
from itertools import groupby


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    license_trailer = fields.Char(string="License Trailer")
    carrier_id = fields.Many2one('res.partner', string="Carrier")


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def default_get(self, default_fields):
        res = super(Picking, self).default_get(default_fields)
        picking_type_id = self.env['stock.picking.type'].search([("code", "=", "internal")])
        if picking_type_id:
            ctx = dict(self._context or {})
            if ctx.get('delivery'):
                res.update({'picking_type_id': picking_type_id[0].id})
        return res

    @api.model
    def create(self, vals):
        if vals.get('origin'):
            purchase_brw = self.env['purchase.order'].search([('name', '=', vals.get('origin'))])
            if purchase_brw:
                if purchase_brw.source_location_id:
                    vals['location_id'] = purchase_brw.source_location_id.id
                if purchase_brw.destination_location_id:
                    vals['location_dest_id'] = purchase_brw.destination_location_id.id
        result = super(Picking, self).create(vals)
        return result


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vehicle_ids = fields.One2many('fleet.vehicle', 'carrier_id', string="Vehicles")
    vehicle_count = fields.Integer("Opportunity", compute='_compute_vehicle_count')

    @api.multi
    def _compute_vehicle_count(self):
        for partner in self:
            partner.vehicle_count = self.env['fleet.vehicle'].search_count([('carrier_id', '=', partner.id)])

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        if context.get('default_is_vendor_service'):
            args += [('is_vendor_service', '=', True)]
        return super(ResPartner, self).search(args, offset, limit, order, count=count)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        context = self._context
        if 'show_carrier' in context:
            if args is None:
                args = []
            args += ([('is_company', '=', True)])
        return super(ResPartner, self).name_search(name=name, args=args, operator=operator, limit=limit)


class Purchaseorder(models.Model):
    _inherit = 'purchase.order'

    purchase_type = fields.Selection([('minor', 'Minor Purchases'), ('complex', 'Complex Purchases'), ],
                                     'Type of Purchase')
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', readonly=True, required=True,
                                          compute='_delivery_address', states={
            'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                          help="Delivery address for current sales order.")

    @api.depends('partner_id')
    def _delivery_address(self):
        for order in self:
            partner_obj = self.env['res.partner']
            search_productor_partner_ids = partner_obj.search([('type', '=', 'center'), (
                'center_type', '=', 'producer'), ('parent_id', '=', order.partner_id and order.partner_id.id or False)])
            order.update({
                'partner_shipping_id': search_productor_partner_ids and search_productor_partner_ids[0].id,
            })

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'check_compliance']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.user.company_id.currency_id.compute(
                        order.company_id.po_double_validation_amount, order.currency_id)) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True


class PurchaseorderLine(models.Model):
    _inherit = 'purchase.order.line'

    lot_ids = fields.Many2many('stock.production.lot', 'lot_purchase_line_rel', 'lot_id', 'purchase_line_id', 'Barcode')
    state = fields.Selection(related='order_id.state', store=True)
    barcode_number = fields.Text('Lot/Barcode')

    @api.model
    def create(self, vals):
        lot_obj = self.env['stock.production.lot']
        search_product = self.env['product.product'].browse(vals.get('product_id'))
        error_messages = list()
        if vals.get('barcode_number'):
            spilt_value = vals.get('barcode_number').split('\n')
            barcode_value = spilt_value
            if barcode_value:
                search_lot_ids = lot_obj.search([('name', 'in', barcode_value)])
                if search_lot_ids:
                    list_lot = [i.id for i in search_lot_ids]
                    self.env.cr.execute('select * from lot_purchase_line_rel where purchase_line_id in %s',
                                        (tuple(list_lot),))
                    result = self.env.cr.dictfetchall()
                    if result:
                        for code in result:
                            brw_lot = lot_obj.browse(code.get('purchase_line_id'))
                            brw_line = self.browse(code.get('lot_id'))
                            error_messages.append(
                                _("código de barras '%s' ya se usa en orden '%s' ,")
                                % (brw_lot.name, brw_line.order_id.name))
                        if error_messages:
                            raise UserError(error_messages)
                    if search_product[0].tracking == 'serial':
                        if vals.get('product_qty') > len(search_lot_ids):
                            raise UserError(
                                _("la cantidad del producto de '%s' no puede ser más que el código de barras") % (
                                    search_product[0].name))
                        elif vals.get('product_qty') < len(search_lot_ids):
                            raise UserError(
                                _("la cantidad del producto de '%s' no puede ser inferior al código de barras") % (
                                    search_product[0].name))
                    vals['lot_ids'] = [(6, 0, list_lot)]
                else:
                    raise UserError(
                        _("barcode '%s' not in system") % (
                            barcode_value))
        if not vals.get('barcode_number'):
            raise UserError(_("por favor agregue código de barras en este producto '%s' ") % (search_product[0].name))
        res = super(PurchaseorderLine, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        print ("*********************self******",self)
        lot_obj = self.env['stock.production.lot']
        if vals.get('barcode_number'):
            spilt_value = vals.get('barcode_number').split('\n')
            barcode_value = spilt_value
            if barcode_value:
                search_lot_ids = lot_obj.search([('name', 'in', barcode_value)])
                if search_lot_ids:
                    if self.product_id.tracking == 'serial':
                        if self.product_qty > len(search_lot_ids):
                            raise UserError(
                                _("la cantidad del producto de '%s' no puede ser más que el código de barras") % (
                                    self.product_id.name))
                        elif self.product_qty < len(search_lot_ids):
                            raise UserError(
                                _("la cantidad del producto de '%s' no puede ser inferior al código de barras") % (
                                    self.product_id.name))
                    vals['lot_ids'] = [(6, 0, [i.id for i in search_lot_ids])]
        for line in self:
            if line.barcode_number and not line.lot_ids:
                spilt_value = line.barcode_number.split('\n')
                barcode_value = spilt_value
                if barcode_value:
                    search_lot_ids = lot_obj.search([('name', 'in', barcode_value)])
                    if search_lot_ids:
                        if line.product_qty > len(search_lot_ids):
                            raise UserError(
                                _("la cantidad del producto de '%s' no puede ser más que el código de barras") % (
                                    line.product_id.name))
                        elif line.product_qty < len(search_lot_ids):
                            raise UserError(
                                _("la cantidad del producto de '%s' no puede ser inferior al código de barras") % (
                                    line.product_id.name))
                        line.lot_ids = [(6, 0, [i.id for i in search_lot_ids])]
        res = super(PurchaseorderLine, self).write(vals)
        return res

    @api.onchange('lot_ids')
    def onchange_lot_ids(self):
        if self.lot_ids:
            if len(self.lot_ids) > self.product_qty:
                raise ValidationError("No puede agregar más código de barras que la cantidad de producto")

    @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        ctx = self._context
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        for move in self.move_ids.filtered(
                lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        if self.lot_ids:
            for lot in self.lot_ids:
                if lot.product_id.id != self.product_id.id:
                    lot.product_id = self.product_id.id
        template = {
            'name': self.name or '',
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'lot_ids': [(6, 0, [i.id for i in self.lot_ids])],
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [
                (6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
        }
        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0, precision_rounding=self.product_uom.rounding) > 0:
            quant_uom = self.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if self.product_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = self.product_uom._compute_quantity(diff_quantity, quant_uom, rounding_method='HALF-UP')
                template['product_uom'] = quant_uom.id
                template['product_uom_qty'] = product_qty
            else:
                template['product_uom_qty'] = diff_quantity
            res.append(template)
        return res


class Stockmove(models.Model):
    _inherit = 'stock.move'

    def _update_reserved_quantity(self, need, available_quantity, location_id, lot_id=None, package_id=None,
                                  owner_id=None, strict=True):
        """ Create or update move lines.
        """
        self.ensure_one()

        if not lot_id:
            lot_id = self.env['stock.production.lot']
        if not package_id:
            package_id = self.env['stock.quant.package']
        if not owner_id:
            owner_id = self.env['res.partner']

        taken_quantity = min(available_quantity, need)
        print("===========available_quantity, need=====", available_quantity, need)
        # `taken_quantity` is in the quants unit of measure. There's a possibility that the move's
        # unit of measure won't be respected if we blindly reserve this quantity, a common usecase
        # is if the move's unit of measure's rounding does not allow fractional reservation. We chose
        # to convert `taken_quantity` to the move's unit of measure with a down rounding method and
        # then get it back in the quants unit of measure with an half-up rounding_method. This
        # way, we'll never reserve more than allowed. We do not apply this logic if
        # `available_quantity` is brought by a chained move line. In this case, `_prepare_move_line_vals`
        # will take care of changing the UOM to the UOM of the product.
        if not strict:
            taken_quantity_move_uom = self.product_id.uom_id._compute_quantity(taken_quantity, self.product_uom,
                                                                               rounding_method='HALF-UP')
            taken_quantity = self.product_uom._compute_quantity(taken_quantity_move_uom, self.product_id.uom_id,
                                                                rounding_method='HALF-UP')
            print("*****************************", taken_quantity_move_uom, taken_quantity)
        quants = []
        print("========>>>lot_id>>>>>>>>>>", lot_id, taken_quantity, self.product_id.uom_id.rounding)
        if self.product_id.tracking == 'serial':
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(taken_quantity, int(taken_quantity), precision_digits=rounding) != 0:
                taken_quantity = 0
        try:
            if not float_is_zero(taken_quantity, precision_rounding=self.product_id.uom_id.rounding):
                print("===========sale_line_id==========", self.sale_line_id.lot_ids)
                quants = self.env['stock.quant'].with_context(
                    lot_ids=self.sale_line_id.lot_ids)._update_reserved_quantity(
                    self.product_id, location_id, taken_quantity, lot_id=lot_id,
                    package_id=package_id, owner_id=owner_id, strict=strict
                )
        except UserError:
            taken_quantity = 0

        # Find a candidate move line to update or create a new one.
        print("---------quants-------=====", quants)
        for reserved_quant, quantity in quants:
            print("______________reserved_quant, quantity______", reserved_quant, quantity)
            to_update = self.move_line_ids.filtered(lambda m: m.product_id.tracking != 'serial' and
                                                              m.location_id.id == reserved_quant.location_id.id and m.lot_id.id == reserved_quant.lot_id.id and m.package_id.id == reserved_quant.package_id.id and m.owner_id.id == reserved_quant.owner_id.id)
            if to_update:
                to_update[0].with_context(
                    bypass_reservation_update=True).product_uom_qty += self.product_id.uom_id._compute_quantity(
                    quantity, to_update[0].product_uom_id, rounding_method='HALF-UP')
            else:
                if self.product_id.tracking == 'serial':
                    for i in range(0, int(quantity)):
                        self.env['stock.move.line'].create(
                            self._prepare_move_line_vals(quantity=1, reserved_quant=reserved_quant))
                else:
                    self.env['stock.move.line'].create(
                        self._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant))
        return taken_quantity

    # Automatically set lot number
    def _action_assign(self):
        """ Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `product_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """
        assigned_moves = self.env['stock.move']
        available_quantity = 0
        partially_available_moves = self.env['stock.move']
        for move in self.filtered(lambda m: m.state in ['confirmed', 'waiting', 'partially_available']):
            print("==========================", move.product_uom_qty, move.reserved_availability)
            missing_reserved_uom_quantity = move.product_uom_qty - move.reserved_availability
            missing_reserved_quantity = move.product_uom._compute_quantity(missing_reserved_uom_quantity,
                                                                           move.product_id.uom_id,
                                                                           rounding_method='HALF-UP')
            if move.location_id.should_bypass_reservation() \
                    or move.product_id.type == 'consu':
                # create the move line(s) but do not impact quants
                if move.product_id.tracking == 'serial' and (
                        move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots):

                    for i, lot in zip(range(0, int(missing_reserved_quantity)), move.lot_ids):
                        self.env['stock.move.line'].create(
                            move.with_context(lot=lot)._prepare_move_line_vals(quantity=1))
                else:
                    to_update = move.move_line_ids.filtered(lambda ml: ml.product_uom_id == move.product_uom and
                                                                       ml.location_id == move.location_id and
                                                                       ml.location_dest_id == move.location_dest_id and
                                                                       ml.picking_id == move.picking_id and
                                                                       not ml.lot_id and
                                                                       not ml.package_id and
                                                                       not ml.owner_id)
                    print ("********to_update*******",to_update )
                    if to_update:
                        to_update[0].product_uom_qty += missing_reserved_uom_quantity
                    else:
                        if move.lot_ids:
                            if len(move.lot_ids) == 1:
                                move_line = self.env['stock.move.line'].create(move.with_context(lot= move.lot_ids)._prepare_move_line_vals(quantity=missing_reserved_quantity))
                                print ("_________move_line___________",move_line.product_qty ,  move_line.product_id.name, move_line.lot_name )
                        else:
                            self.env['stock.move.line'].create(
                                move._prepare_move_line_vals(quantity=missing_reserved_quantity))
                assigned_moves |= move
            else:
                print ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                if not move.move_orig_ids:
                    if move.sale_line_id.lot_ids:
                        for i, lot in zip(range(0, int(missing_reserved_quantity)), move.sale_line_id.lot_ids):
                            search_move_line = self.env['stock.move.line'].search([('lot_id', '=', lot[0].id)])
                            if not search_move_line:
                                self.env['stock.move.line'].create(
                                    move.with_context(lot=lot)._prepare_move_line_vals(quantity=1))
                    if move.procure_method == 'make_to_order':
                        continue
                    # If we don't need any quantity, consider the move assigned.
                    need = missing_reserved_quantity
                    if float_is_zero(need, precision_rounding=move.product_id.uom_id.rounding):
                        assigned_moves |= move
                        continue
                    # Reserve new quants and create move lines accordingly.
                    if move.sale_line_id.lot_ids:
                        available_quantity = self.env['stock.quant'].with_context(
                            lot_ids=move.sale_line_id.lot_ids)._get_available_quantity(move.product_id,
                                                                                       move.location_id)
                    else:
                        available_quantity = self.env['stock.quant']._get_available_quantity(move.product_id,
                                                                                             move.location_id)
                    if available_quantity <= 0:
                        continue
                    taken_quantity = move._update_reserved_quantity(need, available_quantity, move.location_id,
                                                                    strict=False)
                    if float_is_zero(taken_quantity, precision_rounding=move.product_id.uom_id.rounding):
                        continue
                    if need == taken_quantity:
                        assigned_moves |= move
                    else:
                        partially_available_moves |= move

                else:
                    # Check what our parents brought and what our siblings took in order to
                    # determine what we can distribute.
                    # `qty_done` is in `ml.product_uom_id` and, as we will later increase
                    # the reserved quantity on the quants, convert it here in
                    # `product_id.uom_id` (the UOM of the quants is the UOM of the product).
                    move_lines_in = move.move_orig_ids.filtered(lambda m: m.state == 'done').mapped('move_line_ids')
                    keys_in_groupby = ['location_dest_id', 'lot_id', 'result_package_id', 'owner_id']

                    def _keys_in_sorted(ml):
                        return (ml.location_dest_id.id, ml.lot_id.id, ml.result_package_id.id, ml.owner_id.id)

                    grouped_move_lines_in = {}
                    for k, g in groupby(sorted(move_lines_in, key=_keys_in_sorted), key=itemgetter(*keys_in_groupby)):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
                        grouped_move_lines_in[k] = qty_done
                    move_lines_out_done = (move.move_orig_ids.mapped('move_dest_ids') - move) \
                        .filtered(lambda m: m.state in ['done']) \
                        .mapped('move_line_ids')
                    # As we defer the write on the stock.move's state at the end of the loop, there
                    # could be moves to consider in what our siblings already took.
                    moves_out_siblings = move.move_orig_ids.mapped('move_dest_ids') - move
                    moves_out_siblings_to_consider = moves_out_siblings & (assigned_moves + partially_available_moves)
                    reserved_moves_out_siblings = moves_out_siblings.filtered(
                        lambda m: m.state in ['partially_available', 'assigned'])
                    move_lines_out_reserved = (reserved_moves_out_siblings | moves_out_siblings_to_consider).mapped(
                        'move_line_ids')
                    keys_out_groupby = ['location_id', 'lot_id', 'package_id', 'owner_id']

                    def _keys_out_sorted(ml):
                        return (ml.location_id.id, ml.lot_id.id, ml.package_id.id, ml.owner_id.id)

                    grouped_move_lines_out = {}
                    for k, g in groupby(sorted(move_lines_out_done, key=_keys_out_sorted),
                                        key=itemgetter(*keys_out_groupby)):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
                        grouped_move_lines_out[k] = qty_done
                    for k, g in groupby(sorted(move_lines_out_reserved, key=_keys_out_sorted),
                                        key=itemgetter(*keys_out_groupby)):
                        grouped_move_lines_out[k] = sum(
                            self.env['stock.move.line'].concat(*list(g)).mapped('product_qty'))
                    available_move_lines = {key: grouped_move_lines_in[key] - grouped_move_lines_out.get(key, 0) for key
                                            in grouped_move_lines_in.keys()}
                    # pop key if the quantity available amount to 0
                    available_move_lines = dict((k, v) for k, v in available_move_lines.items() if v)

                    if not available_move_lines:
                        continue
                    for move_line in move.move_line_ids.filtered(lambda m: m.product_qty):
                        if available_move_lines.get((move_line.location_id, move_line.lot_id,
                                                     move_line.result_package_id, move_line.owner_id)):
                            available_move_lines[(move_line.location_id, move_line.lot_id, move_line.result_package_id,
                                                  move_line.owner_id)] -= move_line.product_qty
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items():
                        need = move.product_qty - sum(move.move_line_ids.mapped('product_qty'))
                        # `quantity` is what is brought by chained done move lines. We double check
                        # here this quantity is available on the quants themselves. If not, this
                        # could be the result of an inventory adjustment that removed totally of
                        # partially `quantity`. When this happens, we chose to reserve the maximum
                        # still available. This situation could not happen on MTS move, because in
                        # this case `quantity` is directly the quantity on the quants themselves.
                        available_quantity = self.env['stock.quant']._get_available_quantity(
                            move.product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id,
                            strict=True)
                        if float_is_zero(available_quantity, precision_rounding=move.product_id.uom_id.rounding):
                            continue
                        taken_quantity = move._update_reserved_quantity(need, min(quantity, available_quantity),
                                                                        location_id, lot_id, package_id, owner_id)
                        if float_is_zero(taken_quantity, precision_rounding=move.product_id.uom_id.rounding):
                            continue
                        if need - taken_quantity == 0.0:
                            assigned_moves |= move
                            break
                        partially_available_moves |= move
        partially_available_moves.write({'state': 'partially_available'})
        assigned_moves.write({'state': 'assigned'})
        self.mapped('picking_id')._check_entire_pack()

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        self.ensure_one()
        # apply put away
        print("======quantity===", quantity, reserved_quant)
        ctx = self._context
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
        print("=====ctx.get('lot')======",ctx.get('lot'))
        if ctx.get('lot'):
            print ("===========")
            lot_id = ctx.get('lot')
            vals['lot_name'] = lot_id[0].name
            vals['lot_id'] = lot_id[0].id
            vals['qty_done'] = quantity
            # lot_id.sudo().unlink()
        if quantity:
            uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom,
                                                                    rounding_method='HALF-UP')
            uom_quantity_back_to_product_uom = self.product_uom._compute_quantity(uom_quantity, self.product_id.uom_id,
                                                                                  rounding_method='HALF-UP')
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                vals = dict(vals, product_uom_qty=uom_quantity)
            else:
                vals = dict(vals, product_uom_qty=quantity, product_uom_id=self.product_id.uom_id.id)
        if reserved_quant:
            if self.product_id.tracking == 'serial':
                product_vals = {'uncode': self.product_id.uncode or False,
                                'lercode_id': self.product_id.lercode_id.id or False,
                                'admission_parameters': self.product_id.admission_parameters or False,
                                'treatement_operation_ids': self.product_id.treatement_operation_ids.ids,
                                'danger_char_ids': self.product_id.danger_char_ids.ids,
                                'attribute_line_ids': self.product_id.product_tmpl_id.attribute_line_ids
                                }
                reserved_quant.lot_id.write(product_vals)
            vals = dict(
                vals,
                location_id=reserved_quant.location_id.id,
                lot_id=reserved_quant.lot_id.id or False,
                qty_done=1,
                package_id=reserved_quant.package_id.id or False,
                owner_id=reserved_quant.owner_id.id or False,
            )

        return vals


