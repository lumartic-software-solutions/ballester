from odoo import api, fields, models, _
import dateutil.parser
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

# coding=utf-8


class CollectionOrder(models.Model):
    """Collection Order"""
    _inherit = "collection.order"

    teixo_nt_count = fields.Integer("# NTs", compute='_compute_teixont_count')
    teixo_ct_count = fields.Integer("# CTs", compute='_compute_teixoct_count')
    teixo_di_count = fields.Integer("# DIs", compute='_compute_teixodi_count')
    carrier_id = fields.Many2one('res.partner', domain=[
                                 ('type', '=', 'center'),
                                 ('center_type', '=', 'carrier')], string="Transportista" ,  required=True)
    driver_id = fields.Many2one('res.partner', domain=[
        ('type', '=', 'contact')], string="Driver")
    vehicle_id = fields.Many2one('fleet.vehicle', sting="Vehicle")

    @api.onchange('carrier_id')
    def onchange_carrier_id(self):
        fleet_obj = self.env['fleet.vehicle']
        if self.carrier_id:
            partner = self.carrier_id.parent_id
            vehicle_id = fleet_obj.search(
                [('carrier_id', '=', partner.id)])
            if vehicle_id:
                self.vehicle_id = vehicle_id[0].id
                self.driver_id = self.vehicle_id.driver_id and self.vehicle_id.driver_id.id

    @api.multi
    def _compute_teixont_count(self):
        partner = self.partner_id.id
        order_date = dateutil.parser.parse(self.date_order).date()
        residue_ids = [x.product_id.id for x in self.collection_line_ids]
        lines = [y.id for y in self.collection_line_ids]
        partner_ids  = self.env['res.partner'].search([('parent_id','=', partner)])
        productor_center_id = False
        if partner_ids:
            productor_center_id = [i.id for i in  partner_ids]
        else:
            productor_center_id = [partner]
        nt_domain = [('doc_type', '=', 'nt'),
                     ('doc_source', '=', 'annual'),
                     ('productor_center_id', 'in', productor_center_id),
                     '|',
                     ('date_transfer', '<=', order_date),
                     ('date_validity', '>=', order_date),
                     ('residue_id', 'in', residue_ids)]
        nt_domain_lines = [('collection_line_id', 'in', lines),
                           ('doc_type', '=', 'nt')]
        teixo_nt_count = self.env['document.teixo'].search_count(
            nt_domain_lines)
        teixo_nt_count += self.env['document.teixo'].search_count(
            nt_domain)
        self.teixo_nt_count = teixo_nt_count

    @api.multi
    def _compute_teixoct_count(self):
        partner = self.partner_id.id
        lines = [y.id for y in self.collection_line_ids]
        residue_ids = [x.product_id.id for x in self.collection_line_ids]
        order_date = dateutil.parser.parse(self.date_order).date()
        partner_ids  = self.env['res.partner'].search([('parent_id','=', partner)])
        productor_center_id = False
        if partner_ids:
            productor_center_id = [i.id for i in  partner_ids]
        else:
            productor_center_id = [partner]
        ct_domain = [('doc_type', '=', 'ct'),
                     ('doc_source', '=', 'annual'),
                     ('productor_center_id', 'in', productor_center_id),
                     '|',
                     ('date_transfer', '<=', order_date),
                     ('date_validity', '>=', order_date),
                     ('productor_residue_id', 'in', residue_ids)]
        ct_domain_lines = [('collection_line_id', 'in', lines),
                           ('doc_type', '=', 'ct')]
        teixo_ct_count = self.env['document.teixo'].search_count(
            ct_domain_lines)
        teixo_ct_count += self.env['document.teixo'].search_count(
            ct_domain)
        self.teixo_ct_count = teixo_ct_count

    @api.multi
    def _compute_teixodi_count(self):
        partner = self.partner_id.id
        partner_ids  = self.env['res.partner'].search([('parent_id','=', partner)])
        productor_center_id = False
        if partner_ids:
            productor_center_id = [i.id for i in  partner_ids]
        else:
            productor_center_id = [partner]
        residue_ids = [x.product_id.id for x in self.collection_line_ids]
        di_domain = [('doc_type', '=', 'di'),
                     ('productor_center_id', 'in', productor_center_id),
                     ('productor_residue_id', 'in', residue_ids),
                     ('collection_line_id', 'in', [x.id for x in self.collection_line_ids])]
        self.teixo_di_count = self.env['document.teixo'].search_count(
            di_domain)

    @api.multi
    def button_teixont_documents(self):
        partner = self.partner_id.id
        lines = [y.id for y in self.collection_line_ids]
        order_date = dateutil.parser.parse(self.date_order).date()
        residue_ids = [x.product_id.id for x in self.collection_line_ids]
        partner_ids  = self.env['res.partner'].search([('parent_id','=', partner)])
        productor_center_id = False
        if partner_ids:
            productor_center_id = [i.id for i in  partner_ids]
        else:
            productor_center_id = [partner]
        nt_domain = [('doc_type', '=', 'nt'),
                     ('doc_source', '=', 'annual'),
                     ('productor_center_id', 'in', productor_center_id),
                     '|',
                     ('date_transfer', '<=', order_date),
                     ('date_validity', '>=', order_date),
                     ('residue_id', 'in', residue_ids)]
        nt_domain_lines = [('collection_line_id', 'in', lines),
                           ('doc_type', '=', 'nt')]
        doc_ids = self.env['document.teixo'].search(
            nt_domain_lines)
        doc_ids += self.env['document.teixo'].search(nt_domain)
        return {
            'name': _('Teixo Documents(NT)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.teixo',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', doc_ids.ids)],
            'context': self._context, }

    @api.multi
    def button_teixoct_documents(self):
        partner = self.partner_id.id
        lines = [y.id for y in self.collection_line_ids]
        order_date = dateutil.parser.parse(self.date_order).date()
        partner_ids  = self.env['res.partner'].search([('parent_id','=', partner)])
        residue_ids = [x.product_id.id for x in self.collection_line_ids]
        productor_center_id = False
        if partner_ids:
            productor_center_id = [i.id for i in  partner_ids]
        else:
            productor_center_id = [partner]
        ct_domain = [('doc_type', '=', 'ct'),
                     ('doc_source', '=', 'annual'),
                     '|',
                     ('date_transfer', '<=', order_date),
                     ('date_validity', '>=', order_date),
                     ('productor_center_id', 'in', productor_center_id),
                     ('productor_residue_id', 'in', residue_ids)]
        ct_domain_lines = [('collection_line_id', 'in', lines),
                           ('doc_type', '=', 'ct')]
        doc_ids = self.env['document.teixo'].search(
            ct_domain_lines)
        doc_ids += self.env['document.teixo'].search(ct_domain)
        return {
            'name': _('Teixo Documents(CT)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.teixo',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', doc_ids.ids)],
            'context': self._context, }

    @api.multi
    def button_teixodi_documents(self):
        partner = self.partner_id.id
        residue_ids = [x.product_id.id for x in self.collection_line_ids]
        productor_center_id = False
        partner_ids  = self.env['res.partner'].search([('parent_id','=', partner)])
        if partner_ids:
            productor_center_id = [i.id for i in  partner_ids]
        else:
            productor_center_id = [partner]
        di_domain = [('doc_type', '=', 'di'),
                     ('productor_center_id', 'in', productor_center_id),
                     ('productor_residue_id', 'in', residue_ids),
                     ('collection_line_id', 'in', [x.id for x in self.collection_line_ids])]
        doc_ids = self.env['document.teixo'].search(di_domain)
        return {
            'name': _('Teixo Documents(DI)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.teixo',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', doc_ids.ids)],
            'context': self._context, }

    @api.multi
    def action_process(self):
        teixo_obj = self.env['document.teixo']
        product_obj = self.env['product.template']
        partner_obj = self.env['res.partner']
        error_messages = []
        error_message = ''
        order_date = dateutil.parser.parse(self.date_order).date()
        partner_id =  self.partner_id.id
        productor_center_id = False
        partner_ids  = self.env['res.partner'].search([('parent_id','=', partner_id)])
        if partner_ids:
            productor_center_id = [i.id for i in  partner_ids]
        else:
            productor_center_id = [partner]
        for line_vals in self.collection_line_ids:
            residue_id = line_vals.product_id and line_vals.product_id.id
            
            sddr_ids = self.env.ref('ballester_wash.product_param_1_id')
            
            
            nt_domain = [('doc_type', '=', 'nt'),
                         ('productor_center_id', 'in', productor_center_id),
                         '|',
                         ('date_transfer', '<', order_date),
                         ('date_validity', '>', order_date),
                         ('residue_id', '=', residue_id)]
            nt = teixo_obj.search(nt_domain)
            if not nt  and self.purchase_type != 'minor': 
                error_messages.append("No NT found for the vendor %s with product %s and for the date %s." % (
                    partner_obj.browse(partner_id).name, product_obj.browse(residue_id).name, order_date))
            ct_domain = [('doc_type', '=', 'ct'),
                         ('productor_center_id', 'in', productor_center_id),
                         ('productor_residue_id', '=', residue_id)]

            ct = teixo_obj.search(ct_domain)
            if not ct and self.purchase_type != 'minor':
                '''if self.sales_type == 'sddr':
                    raise ValidationError(_("No CT found for the vendor %s with product %s." % (
                     partner_obj.browse(partner_id).name, product_obj.browse(residue_id).name)))''' 
                error_messages.append("No CT found for the vendor %s with product %s." % (
                    partner_obj.browse(partner_id).name, product_obj.browse(residue_id).name))
            di_domain = [('doc_type', '=', 'di'),
                         ('productor_center_id', 'in', productor_center_id),
                         ('productor_residue_id', '=', residue_id),
                         ('collection_line_id', '=', line_vals.id)]
            di = teixo_obj.search(di_domain)
            if not di  and self.purchase_type != 'minor':
                error_messages.append("No DI found for the vendor %s with product %s for current collection order." % (
                    partner_obj.browse(partner_id).name, product_obj.browse(residue_id).name))
        for i, em in enumerate(error_messages):
            error_message += '(' + str(i + 1) + ') ' + em + ' \n'
        if error_message != '':
            raise ValidationError(_(error_message))
        return self.write({'state': 'in_process'})

    @api.multi
    def action_pickup(self):
        if self.collection_type == 'purchase':
            purchase_vals = {'partner_id': self.partner_id.id,
                             'company_id': self.company_id.id,
                             'collection_id': self.id,
                             'collection_line_ids': [(6, 0, [i.id for i in self.collection_line_ids])],
                             'purchase_type': self.purchase_type,
                             'carrier_sale_id': self.carrier_id and self.carrier_id.id,
                             'driver_id': self.driver_id and self.driver_id.id,
                             'transportation_name': self.vehicle_id and self.vehicle_id.id
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
                         'carrier_sale_id': self.carrier_id and self.carrier_id.id,
                         'driver_id': self.driver_id and self.driver_id.id,
                         'transportation_name': self.vehicle_id and self.vehicle_id.id
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

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'collection.order') or _('New')
        result = super(CollectionOrder, self).create(vals)
        return result
