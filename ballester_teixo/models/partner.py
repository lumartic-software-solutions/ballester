from odoo import api, fields, models, _
# coding=utf-8


class Partner(models.Model):
    """Partner"""
    _inherit = "res.partner"


    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            partner.company_type = 'company' if partner.is_company else 'person'


    def _write_company_type(self):
        for partner in self:
            partner.is_company = partner.company_type == 'company'

    @api.model
    def default_get(self, fields):
        result = super(Partner, self).default_get(fields)
        external_code = self.env['ir.sequence'].next_by_code('res.center') or _('New')
        result['external_code'] = external_code
        return result
    
    
    @api.model
    def _get_center_type(self):
        return [
            ('manager', 'Gastor'),
            ('producer', 'Productor'),
            ('operator', 'Operator'),
            ('exploiter_producer', 'Explotador Productor'),
            ('exploiter_gestor', 'Explotador Gestor'),
            ('carrier', 'Transportista'),
            ('final_manager_1', 'Final Manager 1'),
            ('final_manager_2', 'Final Manager 2'),
            ('final_manager_3', 'Final Manager 3')
        ]

    @api.multi
    def name_get(self):
        res = super(Partner, self).name_get()
        
        dict_res = dict(res)
        list_final = []
        for partner in self:
            list_final.append((partner.id , (partner.center_type or '') + " - " + (partner.hazard_type or '') + " - " + dict_res[partner.id]))
        return list_final

    @api.multi
    def _compute_teixont_count(self):
        for partner in self:
            if partner.type == 'center':
                partner.teixo_nt_count = self.env['document.teixo'].search_count([('doc_type', '=', 'nt'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                                        ('productor_center_id', '=', partner.id),
                                                                        ('operador_center_id', '=', partner.id),
                                                                        ('gestor_center_id', '=', partner.id),
                                                                        ('transportista_center_id', '=', partner.id),
                                                                        ('transportista_center_id', '=', partner.id),
                                                                        ('gestor_final_1_center_id', '=', partner.id),
                                                                        ('gestor_final_2_center_id', '=', partner.id),
                                                                        ('gestor_final_3_center_id', '=', partner.id),
                                                                        ('explotador_productor_center_id', '=', partner.id),
                                                                        ('explotador_gestor_center_id', '=', partner.id),
                                                                        ])
            elif partner.type != 'center':
                centers = [x.id for x in partner.child_ids if x.type == 'center']
                partner.teixo_nt_count = self.env['document.teixo'].search_count([('doc_type', '=', 'nt'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
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
                                                                        ])

    @api.multi
    def button_teixont_documents(self):
        if self.type == 'center':
            doc_ids = self.env['document.teixo'].search([('doc_type', '=', 'nt'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                                        ('productor_center_id', '=', self.id),
                                                                        ('operador_center_id', '=', self.id),
                                                                        ('gestor_center_id', '=', self.id),
                                                                        ('transportista_center_id', '=', self.id),
                                                                        ('transportista_center_id', '=', self.id),
                                                                        ('gestor_final_1_center_id', '=', self.id),
                                                                        ('gestor_final_2_center_id', '=', self.id),
                                                                        ('gestor_final_3_center_id', '=', self.id),
                                                                        ('explotador_productor_center_id', '=', self.id),
                                                                        ('explotador_gestor_center_id', '=', self.id),
                                                                        ])
        elif self.type != 'center':
            centers = [x.id for x in self.child_ids if x.type == 'center']
            doc_ids = self.env['document.teixo'].search([('doc_type', '=', 'nt'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
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
                                                                    ])
        return {
            'name': _('Teixo Documents(NTs)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.teixo',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', doc_ids.ids)],
            'context': self._context, }

    @api.multi
    def _compute_teixoct_count(self):
        for partner in self:
            if partner.type == 'center':
                partner.teixo_ct_count = self.env['document.teixo'].search_count([('doc_type', '=', 'ct'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                                        ('productor_center_id', '=', partner.id),
                                                                        ('operador_center_id', '=', partner.id),
                                                                        ('gestor_center_id', '=', partner.id),
                                                                        ('transportista_center_id', '=', partner.id),
                                                                        ('transportista_center_id', '=', partner.id),
                                                                        ('gestor_final_1_center_id', '=', partner.id),
                                                                        ('gestor_final_2_center_id', '=', partner.id),
                                                                        ('gestor_final_3_center_id', '=', partner.id),
                                                                        ('explotador_productor_center_id', '=', partner.id),
                                                                        ('explotador_gestor_center_id', '=', partner.id),
                                                                        ])
            elif partner.type != 'center':
                centers = [x.id for x in partner.child_ids if x.type == 'center']
                partner.teixo_ct_count = self.env['document.teixo'].search_count([('doc_type', '=', 'ct'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
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
                                                                        ])

    @api.multi
    def button_teixoct_documents(self):
        if self.type == 'center':
            doc_ids = self.env['document.teixo'].search([('doc_type', '=', 'ct'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                                        ('productor_center_id', '=', self.id),
                                                                        ('operador_center_id', '=', self.id),
                                                                        ('gestor_center_id', '=', self.id),
                                                                        ('transportista_center_id', '=', self.id),
                                                                        ('transportista_center_id', '=', self.id),
                                                                        ('gestor_final_1_center_id', '=', self.id),
                                                                        ('gestor_final_2_center_id', '=', self.id),
                                                                        ('gestor_final_3_center_id', '=', self.id),
                                                                        ('explotador_productor_center_id', '=', self.id),
                                                                        ('explotador_gestor_center_id', '=', self.id),
                                                                        ])
        elif self.type != 'center':
            centers = [x.id for x in self.child_ids if x.type == 'center']
            doc_ids = self.env['document.teixo'].search([('doc_type', '=', 'ct'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
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
                                                                    ])
        return {
            'name': _('Teixo Documents(CTs)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.teixo',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', doc_ids.ids)],
            'context': self._context, }
        
    @api.multi
    def _compute_teixodi_count(self):
        for partner in self:
            if partner.type == 'center':
                partner.teixo_di_count = self.env['document.teixo'].search_count([('doc_type', '=', 'di'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                                        ('productor_center_id', '=', partner.id),
                                                                        ('operador_center_id', '=', partner.id),
                                                                        ('gestor_center_id', '=', partner.id),
                                                                        ('transportista_center_id', '=', partner.id),
                                                                        ('transportista_center_id', '=', partner.id),
                                                                        ('gestor_final_1_center_id', '=', partner.id),
                                                                        ('gestor_final_2_center_id', '=', partner.id),
                                                                        ('gestor_final_3_center_id', '=', partner.id),
                                                                        ('explotador_productor_center_id', '=', partner.id),
                                                                        ('explotador_gestor_center_id', '=', partner.id),
                                                                        ])
            elif partner.type != 'center':
                centers = [x.id for x in partner.child_ids if x.type == 'center']
                partner.teixo_di_count = self.env['document.teixo'].search_count([('doc_type', '=', 'di'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
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
                                                                        ])

    @api.multi
    def button_teixodi_documents(self):
        if self.type == 'center':
            doc_ids = self.env['document.teixo'].search([('doc_type', '=', 'di'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                                        ('productor_center_id', '=', self.id),
                                                                        ('operador_center_id', '=', self.id),
                                                                        ('gestor_center_id', '=', self.id),
                                                                        ('transportista_center_id', '=', self.id),
                                                                        ('transportista_center_id', '=', self.id),
                                                                        ('gestor_final_1_center_id', '=', self.id),
                                                                        ('gestor_final_2_center_id', '=', self.id),
                                                                        ('gestor_final_3_center_id', '=', self.id),
                                                                        ('explotador_productor_center_id', '=', self.id),
                                                                        ('explotador_gestor_center_id', '=', self.id),
                                                                        ])
        elif self.type != 'center':
            centers = [x.id for x in self.child_ids if x.type == 'center']
            doc_ids = self.env['document.teixo'].search([('doc_type', '=', 'di'), '|', '|', '|', '|', '|', '|', '|', '|', '|',
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
                                                                    ])
        return {
            'name': _('Teixo Documents(DIs)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.teixo',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', doc_ids.ids)],
            'context': self._context, }

    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice address'),
         ('delivery', 'Shipping address'),
         ('center', 'Center'),
         ('other', 'Other address')], string='Address Type',
        default='contact',
        help="Used to select automatically the right address according to the context in sales and purchases documents.")
    hazard_type = fields.Selection([('hazardous', 'Hazardous'), ('non-hazardous', 'Non-Hazardous')],)
    nima = fields.Char(string="Nima")
    cnae_id = fields.Many2one('res.center.cnae', string="CNAE")
    authorization_code = fields.Char(string='Authorization Code', required=True)
    authorization_code_id = fields.Many2one("res.entity.type", required=True, string='Código tipo entidad')
    external_code = fields.Char(string="Codigo Externo", required=True)
    municipality_code_id = fields.Many2one('res.municipio', string="Municipality Code", required=True)
    code_via_id = fields.Many2one('res.codevia', string="Code Via", required=True)
    foreign_company_id = fields.Many2one('res.partner', string="Empresa Extranjera")
    center_type = fields.Selection(_get_center_type, string="Center Type")
    treatment_id = fields.Many2one('treatement.operation', string="Tratamiento")
#   Teixo related Fields
    cif_nif_nie = fields.Char(string="NIF/CIF/NIE", required=True)
    business_name = fields.Char(related="name", required=True, string="Razon Social")
    lastname_1 = fields.Char(string="Apellido")
    association_type_id = fields.Many2one('res.association.type', string="Codigo Tipo Asociacion", required=True)
    transportaion_form_id = fields.Many2one('res.transport.form', string="Codigo Forma Transporte", required=True)
    transport_type_id = fields.Many2one('res.transport.type', string="Codigo Tipo Transporte", required=True)
    residue_ids = fields.One2many('res.residue.center', 'partner_id', string="Residues", required=True)
    entity = fields.Boolean('Entity')
    teixo_nt_count = fields.Integer("# Of NTs", compute='_compute_teixont_count')
    teixo_ct_count = fields.Integer("# Of CTs", compute='_compute_teixoct_count')
    teixo_di_count = fields.Integer("# Of DIs", compute='_compute_teixodi_count')

class Country(models.Model):
    """Country"""
    _inherit = "res.country"

    code_e3l = fields.Char(string="Código e3l pais Teixo")


class ResAssociationType(models.Model):
    """Association"""
    _name = "res.association.type"
    _rec_name = "code"

    code = fields.Char(string="Code", required=True)
    description = fields.Char(string="Description", required=True)

    @api.multi
    def name_get(self):
        data = []
        for rec in self:
            display_value = rec.code
            display_value += ('-' + rec.description) or ""
            data.append((rec.id, display_value))
        return data

class ResTransportType(models.Model):
    """Transport"""
    _name = "res.transport.type"
    _rec_name = "code"

    code = fields.Char(string="Code", required=True)
    description = fields.Char(string="Description", required=True)

    @api.multi
    def name_get(self):
        data = []
        for rec in self:
            display_value = rec.code
            display_value += ('-' + rec.description) or ""
            data.append((rec.id, display_value))
        return data

class ResTransportForm(models.Model):
    """Transport"""
    _name = "res.transport.form"
    _rec_name = "code"

    code = fields.Char(string="Code", required=True)
    description = fields.Char(string="Description", required=True)

    @api.multi
    def name_get(self):
        data = []
        for rec in self:
            display_value = rec.code
            display_value += ('-' + rec.description) or ""
            data.append((rec.id, display_value))
        return data

