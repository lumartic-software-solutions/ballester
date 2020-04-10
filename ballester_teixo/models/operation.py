from odoo import api, fields, models, _
# coding=utf-8


class Operation(models.Model):
    """Operation"""
    _inherit = "stock.picking"

    teixo_nt_count = fields.Integer("# NTs", compute='_compute_teixont_count')
    teixo_ct_count = fields.Integer("# CTs", compute='_compute_teixoct_count')
    teixo_di_count = fields.Integer("# DIs", compute='_compute_teixodi_count')
    
    @api.multi
    def _compute_teixont_count(self):
        partner = self.partner_id
        centers = [x.id for x in partner.child_ids if x.type == 'center']
        moves = [y.id for y in self.move_lines ]
        self.teixo_nt_count = self.env['document.teixo'].search_count([('doc_type', '=', 'nt'), '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                                ('productor_center_id', 'in', centers),
                                                                ('operador_center_id', 'in', centers),
                                                                ('gestor_center_id', 'in', centers),
                                                                ('transportista_center_id', 'in', centers),
                                                                ('transportista_center_id', 'in', centers),
                                                                ('gestor_final_1_center_id', 'in', centers),
                                                                ('gestor_final_2_center_id', 'in', centers),
                                                                ('gestor_final_3_center_id', 'in', centers),
                                                                ('explotador_productor_center_id', 'in', centers),
                                                                ('explotador_gestor_center_id', 'in', centers),
                                                                ('move_id', 'in', moves),
                                                                ])

    @api.multi
    def _compute_teixoct_count(self):
        partner = self.partner_id
        centers = [x.id for x in partner.child_ids if x.type == 'center']
        moves = [y.id for y in self.move_lines ]
        self.teixo_ct_count = self.env['document.teixo'].search_count([('doc_type', '=', 'ct'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                                ('productor_center_id', 'in', centers),
                                                                ('operador_center_id', 'in', centers),
                                                                ('gestor_center_id', 'in', centers),
                                                                ('transportista_center_id', 'in', centers),
                                                                ('transportista_center_id', 'in', centers),
                                                                ('gestor_final_1_center_id', 'in', centers),
                                                                ('gestor_final_2_center_id', 'in', centers),
                                                                ('gestor_final_3_center_id', 'in', centers),
                                                                ('explotador_productor_center_id', 'in', centers),
                                                                ('explotador_gestor_center_id', 'in', centers),
                                                                ('move_id', 'in', moves),
                                                                ])

    @api.multi
    def _compute_teixodi_count(self):
        moves = [y.id for y in self.move_lines ]
        self.teixo_di_count = self.env['document.teixo'].search_count([('doc_type', '=', 'di'),
                                                                ('move_id', 'in', moves),
                                                                ])


    @api.multi
    def button_teixont_documents(self):
        centers = [x.id for x in self.partner_id.child_ids if x.type == 'center']
        moves = [y.id for y in self.move_lines ]
        doc_ids = self.env['document.teixo'].search([('doc_type', '=', 'nt'), '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                                ('productor_center_id', 'in', centers),
                                                                ('operador_center_id', 'in', centers),
                                                                ('gestor_center_id', 'in', centers),
                                                                ('transportista_center_id', 'in', centers),
                                                                ('transportista_center_id', 'in', centers),
                                                                ('gestor_final_1_center_id', 'in', centers),
                                                                ('gestor_final_2_center_id', 'in', centers),
                                                                ('gestor_final_3_center_id', 'in', centers),
                                                                ('explotador_productor_center_id', 'in', centers),
                                                                ('explotador_gestor_center_id', 'in', centers),
                                                                ('move_id', 'in', moves),
                                                                ])
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
        centers = [x.id for x in self.partner_id.child_ids if x.type == 'center']
        moves = [y.id for y in self.move_lines ]
        doc_ids = self.env['document.teixo'].search([('doc_type', '=', 'ct'), '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                                ('productor_center_id', 'in', centers),
                                                                ('operador_center_id', 'in', centers),
                                                                ('gestor_center_id', 'in', centers),
                                                                ('transportista_center_id', 'in', centers),
                                                                ('transportista_center_id', 'in', centers),
                                                                ('gestor_final_1_center_id', 'in', centers),
                                                                ('gestor_final_2_center_id', 'in', centers),
                                                                ('gestor_final_3_center_id', 'in', centers),
                                                                ('explotador_productor_center_id', 'in', centers),
                                                                ('explotador_gestor_center_id', 'in', centers),
                                                                ('move_id', 'in', moves),
                                                                ])
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
        moves = [y.id for y in self.move_lines ]
        doc_ids = self.env['document.teixo'].search([('doc_type', '=', 'di'), ('move_id', 'in', moves),
                                                                ])
        return {
            'name': _('Teixo Documents(DI)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.teixo',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', doc_ids.ids)],
            'context': self._context, }

