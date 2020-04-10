from odoo import api, fields, models, _
import dateutil.parser

# coding=utf-8


class PurchaseOrder(models.Model):
    """Purchase Order"""

    _inherit = "purchase.order"

    teixo_nt_count = fields.Integer("# NTs", compute='_compute_teixont_count')
    teixo_ct_count = fields.Integer("# CTs", compute='_compute_teixoct_count')
    teixo_di_count = fields.Integer("# DIs", compute='_compute_teixodi_count')
    carrier_sale_id = fields.Many2one('res.partner', domain=[
                                 ('type', '=', 'center'),
                                 ('center_type', '=', 'carrier')], string="Transportista" )
    driver_id = fields.Many2one('res.partner', domain=[
        ('type', '=', 'contact')], string="Driver")

    @api.multi
    def _compute_teixont_count(self):
        for po in self:
            centers = [
                x.id for x in po.partner_id.child_ids if x.type == 'center']
            lines = [y.id for y in po.order_line]
            order_date = dateutil.parser.parse(
                po.date_order).date()
            residue_ids = [
                x.product_id.id for x in po.order_line]
            nt_domain = [('doc_type', '=', 'nt'),
                         ('doc_source', '=', 'annual'),
                         ('productor_center_id', 'in', centers),
                         '|',
                         ('date_transfer', '<=', order_date),
                         ('date_validity', '>=', order_date),
                         ('residue_id', 'in', residue_ids)]
            teixo_nt_count = self.env['document.teixo'].search_count(
                nt_domain)
            nt_domain_lines = [('purchase_line_id', 'in', lines),
                               ('doc_type', '=', 'nt')]
            teixo_nt_count += self.env['document.teixo'].search_count(
                nt_domain_lines)
            if po.collection_id:
                lines = [y.id for y in po.collection_id.collection_line_ids]
                partner = po.collection_id.partner_shipping_id.id
                order_date = dateutil.parser.parse(
                    po.collection_id.date_order).date()
                residue_ids = [
                    x.product_id.id for x in po.collection_id.collection_line_ids]
                nt_domain = [('doc_type', '=', 'nt'),
                             ('doc_source', '=', 'annual'),
                             ('productor_center_id', '=', partner),
                             '|',
                             ('date_transfer', '<=', order_date),
                             ('date_validity', '>=', order_date),
                             ('residue_id', 'in', residue_ids)]
                teixo_nt_count += self.env['document.teixo'].search_count(
                    nt_domain)
                nt_domain_lines = [('collection_line_id', 'in', lines),
                                   ('doc_type', '=', 'nt')]
                teixo_nt_count += self.env['document.teixo'].search_count(
                    nt_domain_lines)
            po.teixo_nt_count = teixo_nt_count

    @api.multi
    def _compute_teixoct_count(self):
        for po in self:
            partner = po.partner_id
            centers = [x.id for x in partner.child_ids if x.type == 'center']
            residue_ids = [
                x.product_id.id for x in po.order_line]
            lines = [y.id for y in po.order_line]
            order_date = dateutil.parser.parse(
                po.date_order).date()
            ct_domain = [('doc_type', '=', 'ct'),
                         ('doc_source', '=', 'annual'),
                         '|',
                         ('date_transfer', '<=', order_date),
                         ('date_validity', '>=', order_date),
                         ('productor_center_id', 'in', centers),
                         ('productor_residue_id', 'in', residue_ids)]
            teixo_ct_count = self.env['document.teixo'].search_count(ct_domain)
            ct_domain_lines = [('purchase_line_id', 'in', lines),
                               ('doc_type', '=', 'ct')]
            teixo_ct_count += self.env['document.teixo'].search_count(
                ct_domain_lines)
            if po.collection_id:
                order_date = dateutil.parser.parse(
                    po.collection_id.date_order).date()
                lines = [y.id for y in po.collection_id.collection_line_ids]
                partner = po.collection_id.partner_shipping_id.id
                residue_ids = [
                    x.product_id.id for x in po.collection_id.collection_line_ids]
                ct_domain = [('doc_type', '=', 'ct'),
                             ('doc_source', '=', 'annual'),
                             '|',
                             ('date_transfer', '<=', order_date),
                             ('date_validity', '>=', order_date),
                             ('productor_center_id', '=', partner),
                             ('productor_residue_id', 'in', residue_ids)]
                teixo_ct_count += self.env['document.teixo'].search_count(
                    ct_domain)
                ct_domain_lines = [('collection_line_id', 'in', lines),
                                   ('doc_type', '=', 'ct')]
                teixo_ct_count += self.env['document.teixo'].search_count(
                    ct_domain_lines)
            po.teixo_ct_count = teixo_ct_count

    @api.multi
    def _compute_teixodi_count(self):
        for po in self:
            lines = [y.id for y in po.order_line]
            teixo_di_count = self.env['document.teixo'].search_count([('doc_type', '=', 'di'),
                                                                      ('purchase_line_id',
                                                                       'in', lines),
                                                                      ])
            if po.collection_id:
                di_domain = [('doc_type', '=', 'di'),
                             ('collection_line_id', 'in', [x.id for x in po.collection_id.collection_line_ids])]
                teixo_di_count += self.env['document.teixo'].search_count(
                    di_domain)
            po.teixo_di_count = teixo_di_count

    @api.multi
    def button_teixont_documents(self):
        centers = [x.id for x in self.partner_id.child_ids if x.type == 'center']
        lines = [y.id for y in self.order_line]
        order_date = dateutil.parser.parse(
            self.date_order).date()
        residue_ids = [
            x.product_id.id for x in self.order_line]
        nt_domain = [('doc_type', '=', 'nt'),
                     ('doc_source', '=', 'annual'),
                     ('productor_center_id', 'in', centers),
                     '|',
                     ('date_transfer', '<=', order_date),
                     ('date_validity', '>=', order_date),
                     ('residue_id', 'in', residue_ids)]
        teixo_nt_ids = self.env['document.teixo'].search(
            nt_domain)
        nt_domain_lines = [('purchase_line_id', 'in', lines),
                           ('doc_type', '=', 'nt')]
        teixo_nt_ids += self.env['document.teixo'].search(
            nt_domain_lines)
        if self.collection_id:
            lines = [y.id for y in self.collection_id.collection_line_ids]
            partner = self.collection_id.partner_shipping_id.id
            order_date = dateutil.parser.parse(
                self.collection_id.date_order).date()
            residue_ids = [
                x.product_id.id for x in self.collection_id.collection_line_ids]
            nt_domain = [('doc_type', '=', 'nt'),
                         ('doc_source', '=', 'annual'),
                         ('productor_center_id', '=', partner),
                         '|',
                         ('date_transfer', '<=', order_date),
                         ('date_validity', '>=', order_date),
                         ('residue_id', 'in', residue_ids)]
            teixo_nt_ids += self.env['document.teixo'].search(
                nt_domain)
            nt_domain_lines = [('collection_line_id', 'in', lines),
                               ('doc_type', '=', 'nt')]
            teixo_nt_ids += self.env['document.teixo'].search(
                nt_domain_lines)
        return {
            'name': _('Teixo Documents(NT)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.teixo',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', teixo_nt_ids.ids)],
            'context': self._context, }

    @api.multi
    def button_teixoct_documents(self):
        partner = self.partner_id
        centers = [x.id for x in partner.child_ids if x.type == 'center']
        order_date = dateutil.parser.parse(
            self.date_order).date()
        residue_ids = [
            x.product_id.id for x in self.order_line]
        lines = [y.id for y in self.order_line]
        ct_domain = [('doc_type', '=', 'ct'),
                     ('doc_source', '=', 'annual'),
                     '|',
                     ('date_transfer', '<=', order_date),
                     ('date_validity', '>=', order_date),
                     ('productor_center_id', 'in', centers),
                     ('productor_residue_id', 'in', residue_ids)]
        teixo_ct_ids = self.env['document.teixo'].search(ct_domain)
        ct_domain_lines = [('purchase_line_id', 'in', lines),
                           ('doc_type', '=', 'ct')]
        teixo_ct_ids += self.env['document.teixo'].search(
            ct_domain_lines)
        if self.collection_id:
            order_date = dateutil.parser.parse(
                self.collection_id.date_order).date()
            lines = [y.id for y in self.collection_id.collection_line_ids]
            partner = self.collection_id.partner_shipping_id.id
            residue_ids = [
                x.product_id.id for x in self.collection_id.collection_line_ids]
            ct_domain = [('doc_type', '=', 'ct'),
                         ('doc_source', '=', 'annual'),
                         '|',
                         ('date_transfer', '<=', order_date),
                         ('date_validity', '>=', order_date),
                         ('productor_center_id', '=', partner),
                         ('productor_residue_id', 'in', residue_ids)]
            teixo_ct_ids += self.env['document.teixo'].search(
                ct_domain)
            ct_domain_lines = [('collection_line_id', 'in', lines),
                               ('doc_type', '=', 'ct')]
            teixo_ct_ids += self.env['document.teixo'].search(
                ct_domain_lines)
        return {
            'name': _('Teixo Documents(CT)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.teixo',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', teixo_ct_ids.ids)],
            'context': self._context, }

    @api.multi
    def button_teixodi_documents(self):
        partner = self.partner_id
        centers = [x.id for x in partner.child_ids if x.type == 'center']
        order_date = dateutil.parser.parse(
            self.date_order).date()
        residue_ids = [
            x.product_id.id for x in self.order_line]
        lines = [y.id for y in self.order_line]
        di_domain = [('doc_type', '=', 'di'),
                     ('doc_source', '=', 'annual'),
                     '|',
                     ('date_transfer', '<=', order_date),
                     ('date_validity', '>=', order_date),
                     ('productor_center_id', 'in', centers),
                     ('productor_residue_id', 'in', residue_ids)]
        teixo_di_ids = self.env['document.teixo'].search(di_domain)
        di_domain_lines = [('purchase_line_id', 'in', lines),
                           ('doc_type', '=', 'di')]
        teixo_di_ids += self.env['document.teixo'].search(
            di_domain_lines)
        if self.collection_id:
            order_date = dateutil.parser.parse(
                self.collection_id.date_order).date()
            lines = [y.id for y in self.collection_id.collection_line_ids]
            partner = self.collection_id.partner_shipping_id.id
            residue_ids = [
                x.product_id.id for x in self.collection_id.collection_line_ids]
            di_domain = [('doc_type', '=', 'di'),
                         ('doc_source', '=', 'annual'),
                         '|',
                         ('date_transfer', '<=', order_date),
                         ('date_validity', '>=', order_date),
                         ('productor_center_id', '=', partner),
                         ('productor_residue_id', 'in', residue_ids)]
            teixo_di_ids += self.env['document.teixo'].search(
                di_domain)
            di_domain_lines = [('collection_line_id', 'in', lines),
                               ('doc_type', '=', 'di')]
            teixo_di_ids += self.env['document.teixo'].search(
                di_domain_lines)
        return {
            'name': _('Teixo Documents(DI)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.teixo',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', teixo_di_ids.ids)],
            'context': self._context, }

    '''@api.multi
    def button_teixodi_documents(self):
        teixo_di_ids = []
        lines = [y.id for y in self.order_line]
        teixo_di_ids = self.env['document.teixo'].search_count([('doc_type', '=', 'di'),
                                                                ('purchase_line_id',
                                                                 'in', lines),
                                                                ])
        if self.collection_id:
            di_domain = [('doc_type', '=', 'di'),
                         ('collection_line_id', 'in', [x.id for x in self.collection_id.collection_line_ids])]
            teixo_di_ids += self.env['document.teixo'].search_count(
                di_domain)
        if teixo_di_ids:
            teixo_di_ids = [teixo_di_ids]
        return {
            'name': _('Teixo Documents(DI)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.teixo',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', teixo_di_ids)],
            'context': self._context, }'''



class PurchaseOrderLine(models.Model):
    """Purchase Order Line"""

    _inherit = "purchase.order.line"


    @api.depends('order_id')
    def _compute_ct(self):
        for line in self:
            search_teixo = self.env['document.teixo'].search([('purchase_line_id','=', line.id)])
            if search_teixo:
                self.ct_document = search_teixo[0].codigo

    ct_document = fields.Char('CT Doc',compute='_compute_ct',)


    
