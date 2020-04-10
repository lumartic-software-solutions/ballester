from odoo import models, fields, _, api
from odoo.exceptions import ValidationError, UserError
from requests.auth import HTTPBasicAuth
import ast
import requests
import json


class DocumentTeixo(models.Model):
    _name = 'document.teixo'
    _rec_name = 'codigo'

    @api.one
    @api.depends('collection_line_id')
    def _compute_collection_ref(self):
        self.collection_sale_id = self.collection_line_id.sale_id or self.collection_line_id.sale_id.id
        self.collection_purchase_id = self.collection_line_id.purchase_id or self.collection_line_id.purchase_id.id

    doc_type = fields.Selection(
        [('ct', 'CT'), ('nt', 'NT'), ('di', 'DI')], string="NT/CT/DI ? ")
    doc_source = fields.Selection([('annual', 'Annual'), ('sale', 'From Sales'), ('purchase', 'From Purchase'),
                                   ('collection', 'From Collection'),
                                   ('operation', 'From Operation')], string="Document Type")
    nt_id = fields.Many2one('document.teixo', string='Related NT', domain=[
                            ('doc_type', '=', 'nt')])
    ct_id = fields.Many2one('document.teixo', string='Related CT', domain=[
                            ('doc_type', '=', 'ct')])
    collection_sale_id = fields.Many2one(
        'sale.order', compute='_compute_collection_ref', store=True, string="Related Sales Order")
    collection_purchase_id = fields.Many2one(
        'purchase.order', compute='_compute_collection_ref', store=True, string="Related Purchase Order")
    productor_center_id = fields.Many2one('res.partner', "Productor Center")
    operador_center_id = fields.Many2one('res.partner', "Operador Center")
    gestor_center_id = fields.Many2one('res.partner', "Gestor Center")
    transportista_center_id = fields.Many2one(
        'res.partner', "Transportista Center")
    explotador_productor_center_id = fields.Many2one(
        'res.partner', "Explotador Productor Center")
    explotador_gestor_center_id = fields.Many2one(
        'res.partner', "Explotador Gestor Center")
    gestor_final_1_center_id = fields.Many2one(
        'res.partner', "Gestor Final 1 Center")
    gestor_final_2_center_id = fields.Many2one(
        'res.partner', "Gestor Final 2 Center")
    gestor_final_3_center_id = fields.Many2one(
        'res.partner', "Gestor Final 3 Center")
    sale_line_id = fields.Many2one(
        'sale.order.line', "Sale Order Line Reference", readonly=1)
    purchase_line_id = fields.Many2one(
        'purchase.order.line', "Purchase Order Line Reference", readonly=1)
    collection_line_id = fields.Many2one(
        'collection.order.line', "Collection Order Line Reference", readonly=1)
    move_id = fields.Many2one('stock.move', "Stock Move Reference", readonly=1)
    codigo = fields.Char("Document Code", copy=False)
    teixo_doc_url = fields.Char("Teixo Document URL", copy=False)
    residue_id = fields.Many2one('product.template', "Residue")
    productor_residue_id = fields.Many2one(
        'product.template', "Productor Residue")
    gestor_residue_id = fields.Many2one('product.template', "Gestor Residue")
    state_di = fields.Selection([('pro_forma', 'Pro Forma'), ('pendiente_aceptacion', 'Pendiente Aceptacion'),
                                 ('cerrado', 'Cerrado')], default='pro_forma', copy=False, string='State')
    estado_admon = fields.Char(copy=False, string='Estado Admon')
    expiration_date = fields.Char('Expiration Date')
    data_admission = fields.Boolean('Datos Admision', default='1')
    consecuencias_legales = fields.Text('Consecuencias Legales')
    parametros_admision = fields.Text('Parametros Admision')
    start_date_di = fields.Date("Fecha Inicio Traslado")
    real_qty = fields.Float(string="Waste Real Quantity")
    acceptance_id = fields.Many2one(
        'res.acceptance', string="Aceptacion Codigo ")
    incedence_id_1 = fields.Many2one(
        'res.incidence', string="Incidencia Codigo 1")
    incedence1_observation = fields.Text("Incidenciao 1 Observaciones")
    incedence_id_2 = fields.Many2one(
        'res.incidence', string="Incidencia Codigo 2")
    incedence2_observation = fields.Text("Incidenciao 2 Observaciones")
    acceptance_date = fields.Date("Aceptacion Fecha")
    date_validity = fields.Date("Fecha Validez")
    date_transfer = fields.Date("Fecha Traslado")
    enviar_admon = fields.Boolean('Enviado a la administración')
    error_envio_admon = fields.Text('Error Envio Admon', default='/')
    document_sent = fields.Boolean('Document Sent to Teixo')
    gross_weight_residue = fields.Float("Residuo Peso Bruto")
    net_weight_residue = fields.Float("Residuo Peso Neto")

    @api.onchange('ct_id')
    def onchange_ct(self):
        if self.ct_id:
            self.productor_center_id = self.ct_id.productor_center_id
            self.gestor_center_id = self.ct_id.gestor_center_id
            self.explotador_gestor_center_id = self.ct_id.explotador_gestor_center_id
            self.explotador_productor_center_id = self.ct_id.explotador_productor_center_id
            self.operador_center_id = self.ct_id.explotador_gestor_center_id
            self.productor_residue_id = self.ct_id.productor_residue_id
            self.gestor_residue_id = self.ct_id.gestor_residue_id

    @api.onchange('nt_id')
    def onchange_nt(self):
        if self.nt_id and self.nt_id.ct_id:
            self.ct_id = self.nt_id.ct_id

#     @api.onchange('productor_residue_id')
#     def onchange_residue(self):
#         print("===onchange_residue====", self.productor_residue_id,
#               self.productor_residue_id.weight)
#         if self.productor_residue_id:
#             self.real_qty = self.productor_residue_id.weight

    @api.model
    def create(self, vals):
        product = self.env['product.template']
        partner = self.env['res.partner']
        gestor = partner.browse(vals.get('gestor_center_id'))
        productor = partner.browse(vals.get('productor_center_id'))
        transportista = partner.browse(vals.get('transportista_center_id'))
        if vals.get('doc_type') == 'di' and vals.get('doc_source') == 'annual':
            raise ValidationError(_("DIs can not be created Annually!"))
        if (vals.get('doc_type') != 'nt') and vals.get('productor_residue_id') and vals.get('gestor_residue_id') and (vals.get('productor_residue_id') != vals.get('gestor_residue_id')):
            raise ValidationError(
                _("Gestor and Productor Residues are different"))
        if (vals.get('doc_type') == 'nt'):
            dangrous = product.browse(
                vals.get('residue_id')).lercode_id.dangerous
        else:
            dangrous = product.browse(
                vals.get('productor_residue_id')).lercode_id.dangerous
        if dangrous:
            if gestor.hazard_type != 'hazardous':
                raise ValidationError(
                    _("Gestor Entity Type Code is not For Hazardous Residue,And Resiude is Hazardous"))
            if productor.hazard_type != 'hazardous':
                raise ValidationError(
                    _("Productor Entity Type Code is not For Hazardous Residue,And Resiude is Hazardous"))
            if transportista.hazard_type != 'hazardous' and (vals.get('doc_type') in ['nt', 'di']):
                raise ValidationError(
                    _("Transportista Entity Type Code is not For Hazardous Residue,And Resiude is Hazardous"))
        if not dangrous:
            if gestor.hazard_type == 'hazardous':
                raise ValidationError(
                    _("Gestor Entity Type Code is not For Non-Hazardous Residue,While Resiude is Non-Hazardous"))
            if productor.hazard_type == 'hazardous':
                raise ValidationError(
                    _("Productor Entity Type Code is not For Non-Hazardous Residue,While Resiude is Non-Hazardous"))
            if transportista.hazard_type == 'hazardous' and (vals.get('doc_type') in ['nt', 'di']):
                raise ValidationError(
                    _("Transportista Entity Type Code is not For Non-Hazardous Residue,While Resiude is Non-Hazardous"))
        result = super(DocumentTeixo, self).create(vals)
        return result

    @api.model
    def default_get(self, default_fields):
        res = super(DocumentTeixo, self).default_get(default_fields)
        ctx = dict(self._context)
        gestor = self.env['res.users'].browse(
            self._uid).company_id.partner_id.id
        if ctx.get('active_model') == 'sale.order.line' and ctx.get('active_id'):
            order_line_id = self.env['sale.order.line'].browse(
                ctx.get('active_id'))
            res.update({'sale_line_id': order_line_id.id,
                        'residue_id': order_line_id.product_id.product_tmpl_id.id,
                        'productor_residue_id': order_line_id.product_id.product_tmpl_id.id,
                        'real_qty': order_line_id.product_id.product_tmpl_id.weight * order_line_id.product_uom_qty,
                        'gross_weight_residue': order_line_id.product_id.product_tmpl_id.weight * order_line_id.product_uom_qty,
                        'net_weight_residue': order_line_id.product_id.product_tmpl_id.weight * order_line_id.product_uom_qty,
                        'gestor_residue_id': order_line_id.product_id.product_tmpl_id.id,
                        'productor_center_id': order_line_id.order_id.partner_id.id,
                        'transportista_center_id': order_line_id.order_id.carrier_sale_id.id,
                        })
        if ctx.get('active_model') == 'stock.move' and ctx.get('active_id'):
            move_id = self.env['stock.move'].browse(
                ctx.get('active_id'))
            res.update({'move_id': ctx.get('active_id'),
                        'residue_id': move_id.product_id.product_tmpl_id.id,
                        'productor_residue_id': move_id.product_id.product_tmpl_id.id,
                        'real_qty': move_id.product_id.product_tmpl_id.weight,
                        'gestor_residue_id': move_id.product_id.product_tmpl_id.id,
                        'productor_center_id': move_id.picking_id.partner_id.id})
        if ctx.get('active_model') == 'purchase.order.line' and ctx.get('active_id'):
            ct_id = False
            order_line_id = self.env['purchase.order.line'].browse(
                ctx.get('active_id'))
            nt_id = False
            productor_center_id = False
            partner_ids  = self.env['res.partner'].search([('parent_id','=', order_line_id.order_id.partner_id.id)])
            if partner_ids:
                productor_center_id =  [i.id for i in partner_ids]
            else:
                productor_center_id = [ order_line_id.order_id.partner_id.id]
            search_teixo = self.search([('productor_center_id','in',productor_center_id),('doc_source', '=', 'annual'),('doc_type','=','ct'),('productor_residue_id','=', order_line_id.product_id.id)])
            if search_teixo:
                ct_id = search_teixo[0].id
            search_nt_teixo = self.search([('productor_center_id','in',productor_center_id),('doc_source', '=', 'annual'),('doc_type','=','nt'),('productor_residue_id','=', order_line_id.product_id.id)])
            res.update({'purchase_line_id': ctx.get('active_id'),
                        'residue_id': order_line_id.product_id.product_tmpl_id.id,
                        'productor_residue_id': order_line_id.product_id.product_tmpl_id.id,
                        'real_qty': order_line_id.product_id.product_tmpl_id.weight * order_line_id.product_qty,
                        'gross_weight_residue': order_line_id.product_id.product_tmpl_id.weight * order_line_id.product_qty,
                        'net_weight_residue': order_line_id.product_id.product_tmpl_id.weight * order_line_id.product_qty,
                        'gestor_residue_id': order_line_id.product_id.product_tmpl_id.id,
                        'productor_center_id': order_line_id.order_id.partner_id.id,
                        'transportista_center_id': order_line_id.order_id.carrier_sale_id.id,
			'ct_id':ct_id,
			'nt_id':nt_id

})
        if ctx.get('active_model') == 'collection.order.line' and ctx.get('active_id'):
            order_line_id = self.env['collection.order.line'].browse(
                ctx.get('active_id'))
            ct_id = False
            nt_id = False
            productor_center_id = False
            partner_ids  = self.env['res.partner'].search([('parent_id','=', order_line_id.order_id.partner_id.id)])
            if partner_ids:
                productor_center_id =  [i.id for i in partner_ids]
            else:
                productor_center_id = [ order_line_id.order_id.partner_id.id]
            search_teixo = self.search([('productor_center_id','in', productor_center_id),('doc_source', '=', 'annual'),('doc_type','=','ct'),('productor_residue_id','=', order_line_id.product_id.id)])
            if search_teixo:
                ct_id = search_teixo[0].id
            search_nt_teixo = self.search([('productor_center_id','in',productor_center_id),('doc_source', '=', 'annual'),('doc_type','=','nt'),('productor_residue_id','=', order_line_id.product_id.id)])
            if search_nt_teixo:
                nt_id = search_nt_teixo[0].id
           
            res.update({'collection_line_id': ctx.get('active_id'),
                        'residue_id': order_line_id.product_id.id,
                        'productor_residue_id': order_line_id.product_id.id,
                        'gestor_residue_id': order_line_id.product_id.id,
                        'productor_center_id': order_line_id.order_id.partner_shipping_id.id,
                        'real_qty': order_line_id.product_id.weight * order_line_id.product_uom_qty,
                        'gross_weight_residue': order_line_id.product_id.weight * order_line_id.product_uom_qty,
                        'net_weight_residue': order_line_id.product_id.weight * order_line_id.product_uom_qty,
                        'transportista_center_id': order_line_id.order_id.carrier_id.id,
			'ct_id':ct_id,
			'nt_id':nt_id })
        res.update({'gestor_center_id': gestor})
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        context = self._context
        ids = []
        if context.get('rdoc_type') == 'nt':
            method_name = 'button_teixont_documents'
        elif context.get('rdoc_type') == 'ct':
            method_name = 'button_teixoct_documents'
        if context.get('rdoc_source') == 'annual':
            partner = self.env['res.partner'].browse(context.get('partner'))
            ids = getattr(partner, method_name)()['domain'][0][2]
        if context.get('rdoc_source') == 'sale':
            so = self.env['sale.order.line'].browse(
                context.get('sale')).order_id
            ids = getattr(so, method_name)()['domain'][0][2]
        if context.get('rdoc_source') == 'purchase':
            po = self.env['purchase.order.line'].browse(
                context.get('purchase')).order_id
            ids = getattr(po, method_name)()['domain'][0][2]
        if context.get('rdoc_source') == 'collection':
            collection = self.env['collection.order.line'].browse(
                context.get('collection')).order_id
            ids = getattr(collection, method_name)()['domain'][0][2]
        if context.get('rdoc_source') == 'operation':
            picking = self.env['stock.move'].browse(
                context.get('move')).picking_id
            ids = getattr(picking, method_name)()['domain'][0][2]
        if args is None:
            args = []
        args += ([('id', 'in', ids)])
        return super(DocumentTeixo, self).name_search(name=name, args=args, operator=operator, limit=limit)

    def connect_teixo(self):
        if self.doc_type == 'nt':
            self.create_nt()
        elif self.doc_type == 'ct':
            self.create_ct()
        elif self.doc_type == 'di':
            self.create_di()
        self.document_sent = True

    def create_nt(self):
        teixo_user_name = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_user', default='')
        teixo_token = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_token', default='')
        api_url = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_url', default='')

        data = self.create_nt_data()
        full_api = api_url + '/nt/'
        headers = {'content-type': 'application/json; charset=utf-8',
                   'Accept': 'application/json'}
        auth = HTTPBasicAuth(str(teixo_user_name), str(teixo_token))
        login_response = requests.post(
            full_api, data=json.dumps(data), headers=headers, auth=auth)
        print ("------------login_response-------",login_response)
        if login_response.__dict__.get('status_code') == 201:
            if '_content' in login_response.__dict__:
                convert_data = login_response.__dict__.get(
                    '_content').decode('utf-8')
                get_data = ast.literal_eval(convert_data)
                if 'codigo' in get_data:
                    self.codigo = get_data.get('codigo') or ''
                if 'url_pdf' in get_data:
                    self.teixo_doc_url = get_data.get('url_pdf') or ''
        else:
            print ("<<<<<<<<<<<login_response.text<<<<<<<<",login_response.text )
            raise UserError(_('%s') % (login_response.text))

    def create_nt_data(self):
        product = self.residue_id
        print ("<<<<<<<<product<<<", product)
        if not product:
            raise ValidationError(_("Please Select Product For Create NT."))
        if product.weight == 0.00:
            raise ValidationError(_("Product Weight Is Zero."))
        table_list = []
        if not product.lot_attribute_line_ids:
            raise ValidationError(
                _("Please Select Atleast One Table In The Product."))
        if not self.transportista_center_id.parent_id.vehicle_ids:
            raise ValidationError(
                _("There is no vehicle available for this transportista ,Please create one."))
        for value in product.lot_attribute_line_ids:
            for tab in value.value_ids:
                split_value = tab.name.split(" ")
                table_list.append(split_value[0])
            all_table = '//'.join(table_list)
        print ("==================all_table========",all_table )

        data = {
            "documento": {
                "actualizar_datos": 'S',
                "fecha_traslado": self.date_transfer,
                "transportista":
                {
                    "nombre": self.transportista_center_id.parent_id.name,
                    "codigo_externo": self.transportista_center_id.parent_id.external_code,
                    "codigo_tipo_transporte": self.transportista_center_id.parent_id.transport_type_id and self.transportista_center_id.parent_id.transport_type_id.code,
                    "cif_nif_nie": self.transportista_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.transportista_center_id.parent_id.business_name,
                    "apellido1": self.transportista_center_id.parent_id.lastname_1,
                    "matricula": self.transportista_center_id.parent_id.vehicle_ids and self.transportista_center_id.parent_id.vehicle_ids[0].license_plate,
                    "codigo_tipo_entidad": self.transportista_center_id.parent_id.authorization_code_id and self.transportista_center_id.parent_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.transportista_center_id.parent_id.association_type_id and self.transportista_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.transportista_center_id.phone,
                            "localidad": self.transportista_center_id.city,
                            "nombre": self.transportista_center_id.name,
                            "nima": self.transportista_center_id.nima,
                            "codigo_municipio": self.transportista_center_id.municipality_code_id and self.transportista_center_id.municipality_code_id.code,
                            "direccion": self.transportista_center_id.street,
                            "email": self.transportista_center_id.email,
                            "codigo_via": self.transportista_center_id.code_via_id and self.transportista_center_id.code_via_id.code,
                            "codigo_postal": self.transportista_center_id.zip,
                            "autorizacion": self.transportista_center_id.authorization_code
                    },
                },
                "residuo":
                {
                    "tablas": all_table,
                    "ler": product.lercode_id.name,
                    "peso": product.weight,
                },
                "gestor":
                {
                    "nombre": self.gestor_center_id.parent_id.name,
                    "codigo_externo": self.gestor_center_id.parent_id.external_code,
                    "cif_nif_nie": self.gestor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.gestor_center_id.parent_id.business_name,
                    "apellido1": self.gestor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.gestor_center_id.authorization_code_id and self.gestor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.gestor_center_id.parent_id.association_type_id and self.gestor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.gestor_center_id.phone,
                            "localidad": self.gestor_center_id.city,
                            "nombre": self.gestor_center_id.name,
                            "nima": self.gestor_center_id.nima,
                            "codigo_municipio": self.gestor_center_id.municipality_code_id and self.gestor_center_id.municipality_code_id.code,
                            "direccion": self.gestor_center_id.street,
                            "email": self.gestor_center_id.email,
                            "codigo_via": self.gestor_center_id.code_via_id and self.gestor_center_id.code_via_id.code,
                            "codigo_postal": self.gestor_center_id.zip,
                            "autorizacion": self.gestor_center_id.authorization_code
                        },
                },
                "productor":
                {
                    "nombre": self.productor_center_id.parent_id.name,
                    "codigo_externo": self.productor_center_id.parent_id.external_code,
                    "cif_nif_nie": self.productor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.productor_center_id.parent_id.business_name,
                    "apellido1": self.productor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.productor_center_id.authorization_code_id and self.productor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.productor_center_id.parent_id.association_type_id and self.productor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.productor_center_id.phone,
                            "localidad": self.productor_center_id.city,
                            "nombre": self.productor_center_id.name,
                            "nima": self.productor_center_id.nima,
                            "codigo_municipio": self.productor_center_id.municipality_code_id and self.productor_center_id.municipality_code_id.code,
                            "direccion": self.productor_center_id.street,
                            "email": self.productor_center_id.email,
                            "codigo_via": self.productor_center_id.code_via_id and self.productor_center_id.code_via_id.code,
                            "codigo_postal": self.productor_center_id.zip,
                            "autorizacion": self.productor_center_id.authorization_code
                        },
                },
            },
        }
        if self.codigo:
            data['documento'].update({'codigo': self.codigo})
        if self.date_validity:
            data['documento'].update({'fecha_validez': self.date_validity})
        if self.ct_id:
            data['documento'].update({'codigo_da': self.ct_id.codigo})
        if self.explotador_gestor_center_id:
            data['documento'].update({
                "                explotador_gestor":
                {
                    "nombre": self.explotador_gestor_center_id.parent_id.name,
                    "codigo_externo": self.explotador_gestor_center_id.parent_id.external_code,
                    "cif_nif_nie": self.explotador_gestor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.explotador_gestor_center_id.parent_id.business_name,
                    "apellido1": self.explotador_gestor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.explotador_gestor_center_id.authorization_code_id and self.explotador_gestor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.explotador_gestor_center_id.parent_id.association_type_id and self.explotador_gestor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.explotador_gestor_center_id.phone,
                            "localidad": self.explotador_gestor_center_id.city,
                            "nombre": self.explotador_gestor_center_id.name,
                            "nima": self.explotador_gestor_center_id.nima,
                            "codigo_municipio": self.explotador_gestor_center_id.municipality_code_id and self.explotador_gestor_center_id.municipality_code_id.code,
                            "direccion": self.explotador_gestor_center_id.street,
                            "email": self.explotador_gestor_center_id.email,
                            "codigo_via": self.explotador_gestor_center_id.code_via_id and self.explotador_gestor_center_id.code_via_id.code,
                            "codigo_postal": self.explotador_gestor_center_id.zip,
                            "autorizacion": self.explotador_gestor_center_id.authorization_code
                        },
                }})
        if self.explotador_productor_center_id:
            data['documento'].update({
                "explotador_productor":
                {
                    "nombre": self.explotador_productor_center_id.parent_id.name,
                    "codigo_externo": self.explotador_productor_center_id.parent_id.external_code,
                    "cif_nif_nie": self.explotador_productor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.explotador_productor_center_id.parent_id.business_name,
                    "apellido1": self.explotador_productor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.explotador_productor_center_id.authorization_code_id and self.explotador_productor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.explotador_productor_center_id.parent_id.association_type_id and self.explotador_productor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.explotador_productor_center_id.phone,
                            "localidad": self.explotador_productor_center_id.city,
                            "nombre": self.explotador_productor_center_id.name,
                            "nima": self.explotador_productor_center_id.nima,
                            "codigo_municipio": self.explotador_productor_center_id.municipality_code_id and self.explotador_productor_center_id.municipality_code_id.code,
                            "direccion": self.explotador_productor_center_id.street,
                            "email": self.explotador_productor_center_id.email,
                            "codigo_via": self.explotador_productor_center_id.code_via_id and self.explotador_productor_center_id.code_via_id.code,
                            "codigo_postal": self.explotador_productor_center_id.zip,
                            "autorizacion": self.explotador_productor_center_id.authorization_code
                        },
                }})
        if self.operador_center_id:
            data['documento'].update({
                "operador":
                    {
                        "nombre": self.operator_center_id.parent_id.name,
                        "codigo_externo": self.operator_center_id.parent_id.external_code,
                        "cif_nif_nie": self.operator_center_id.parent_id.cif_nif_nie,
                        "razon_social": self.operator_center_id.parent_id.business_name,
                        "apellido1": self.operator_center_id.parent_id.lastname_1,
                        "codigo_tipo_entidad": self.operator_center_id.authorization_code_id and self.operator_center_id.authorization_code_id.code,
                        "codigo_tipo_asociacion": self.operator_center_id.parent_id.association_type_id and self.operator_center_id.parent_id.association_type_id.code,
                        "centro":
                        {
                            "telefono": self.operator_center_id.phone,
                            "localidad": self.operator_center_id.city,
                            "nombre": self.operator_center_id.name,
                            "nima": self.operator_center_id.nima,
                            "codigo_municipio": self.operator_center_id.municipality_code_id and self.operator_center_id.municipality_code_id.code,
                            "direccion": self.operator_center_id.street,
                            "email": self.operator_center_id.email,
                            "codigo_via": self.operator_center_id.code_via_id and self.operator_center_id.code_via_id.code,
                            "codigo_postal": self.operator_center_id.zip,
                            "autorizacion": self.operator_center_id.authorization_code
                        },
                    },
            })
        if self.gestor_final_1_center_id:
            data['documento'].update({
                "gestor_final_1":
                    {
                        "nombre": self.gestor_final_1_center_id.parent_id.name,
                        "codigo_externo": self.gestor_final_1_center_id.parent_id.external_code,
                        "cif_nif_nie": self.gestor_final_1_center_id.parent_id.cif_nif_nie,
                        "razon_social": self.gestor_final_1_center_id.parent_id.business_name,
                        "apellido1": self.gestor_final_1_center_id.parent_id.lastname_1,
                        "codigo_tipo_entidad": self.gestor_final_1_center_id.parent_id.authorization_code_id and self.gestor_final_1_center_id.parent_id.authorization_code_id.code,
                        "codigo_tipo_asociacion": self.gestor_final_1_center_id.parent_id.association_type_id and self.gestor_final_1_center_id.parent_id.association_type_id.code,
                        "centro":
                        {
                            "telefono": self.gestor_final_1_center_id.phone,
                            "localidad": self.gestor_final_1_center_id.city,
                            "nombre": self.gestor_final_1_center_id.name,
                            "nima": self.gestor_final_1_center_id.nima,
                            "codigo_municipio": self.gestor_final_1_center_id.municipality_code_id and self.gestor_final_1_center_id.municipality_code_id.code,
                            "direccion": self.gestor_final_1_center_id.street,
                            "email": self.gestor_final_1_center_id.email,
                            "codigo_via": self.gestor_final_1_center_id.code_via_id and self.gestor_final_1_center_id.code_via_id.code,
                            "codigo_postal": self.gestor_final_1_center_id.zip,
                            "autorizacion": self.gestor_final_1_center_id.authorization_code
                        },
                    },
            })
        if self.gestor_final_2_center_id:
            data['documento'].update({
                "gestor_final_2":
                    {
                        "nombre": self.gestor_final_2_center_id.parent_id.name,
                        "codigo_externo": self.gestor_final_2_center_id.parent_id.external_code,
                        "cif_nif_nie": self.gestor_final_2_center_id.parent_id.cif_nif_nie,
                        "razon_social": self.gestor_final_2_center_id.parent_id.business_name,
                        "apellido1": self.gestor_final_2_center_id.parent_id.lastname_1,
                        "codigo_tipo_entidad": self.gestor_final_2_center_id.parent_id.authorization_code_id and self.gestor_final_2_center_id.parent_id.authorization_code_id.code,
                        "codigo_tipo_asociacion": self.gestor_final_2_center_id.parent_id.association_type_id and self.gestor_final_2_center_id.parent_id.association_type_id.code,
                        "centro":
                        {
                            "telefono": self.gestor_final_2_center_id.phone,
                            "localidad": self.gestor_final_2_center_id.city,
                            "nombre": self.gestor_final_2_center_id.name,
                            "nima": self.gestor_final_2_center_id.nima,
                            "codigo_municipio": self.gestor_final_2_center_id.municipality_code_id and self.gestor_final_2_center_id.municipality_code_id.code,
                            "direccion": self.gestor_final_2_center_id.street,
                            "email": self.gestor_final_2_center_id.email,
                            "codigo_via": self.gestor_final_2_center_id.code_via_id and self.gestor_final_2_center_id.code_via_id.code,
                            "codigo_postal": self.gestor_final_2_center_id.zip,
                            "autorizacion": self.gestor_final_2_center_id.authorization_code
                        },
                    },
            })
        if self.gestor_final_3_center_id:
            data['documento'].update({
                "gestor_final_3":
                    {
                        "nombre": self.gestor_final_3_center_id.parent_id.name,
                        "codigo_externo": self.gestor_final_3_center_id.parent_id.external_code,
                        "cif_nif_nie": self.gestor_final_3_center_id.parent_id.cif_nif_nie,
                        "razon_social": self.gestor_final_3_center_id.parent_id.business_name,
                        "apellido1": self.gestor_final_3_center_id.parent_id.lastname_1,
                        "codigo_tipo_entidad": self.gestor_final_3_center_id.parent_id.authorization_code_id and self.gestor_final_3_center_id.parent_id.authorization_code_id.code,
                        "codigo_tipo_asociacion": self.gestor_final_3_center_id.parent_id.association_type_id and self.gestor_final_3_center_id.parent_id.association_type_id.code,
                        "centro":
                        {
                            "telefono": self.gestor_final_3_center_id.phone,
                            "localidad": self.gestor_final_3_center_id.city,
                            "nombre": self.gestor_final_3_center_id.name,
                            "nima": self.gestor_final_3_center_id.nima,
                            "codigo_municipio": self.gestor_final_3_center_id.municipality_code_id and self.gestor_final_3_center_id.municipality_code_id.code,
                            "direccion": self.gestor_final_3_center_id.street,
                            "email": self.gestor_final_3_center_id.email,
                            "codigo_via": self.gestor_final_3_center_id.code_via_id and self.gestor_final_3_center_id.code_via_id.code,
                            "codigo_postal": self.gestor_final_3_center_id.zip,
                            "autorizacion": self.gestor_final_3_center_id.authorization_code
                        },
                    },
            })
        print ("<<<<<<<<<<<<<<xxxxxxfdata",data)
        return data

    def create_ct(self):
        teixo_user_name = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_user', default='')
        teixo_token = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_token', default='')
        api_url = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_url', default='')

        data = self.create_ct_data()
        full_api = api_url + '/ct/'
        headers = {'content-type': 'application/json; charset=utf-8',
                   'Accept': 'application/json'}
        auth = HTTPBasicAuth(str(teixo_user_name), str(teixo_token))
        login_response = requests.post(
            full_api, data=json.dumps(data), headers=headers, auth=auth)
        if login_response.__dict__.get('status_code') == 201:
            if '_content' in login_response.__dict__:
                convert_data = login_response.__dict__.get(
                    '_content').decode('utf-8')
                get_data = ast.literal_eval(convert_data)
                if 'codigo' in get_data:
                    self.codigo = get_data.get('codigo') or ''
                if 'url_pdf' in get_data:
                    self.teixo_doc_url = get_data.get('url_pdf') or ''
        else:
            raise UserError(_('%s') % (login_response.text))

    def create_ct_data(self):
        productor_residue = self.productor_residue_id
        gestor_residue = self.gestor_residue_id
        if not productor_residue or not gestor_residue:
            raise ValidationError(
                _("Please Select Productor Residue and Gestor Residue For Create CT."))
        productor_table_list = []
        if not productor_residue.lot_attribute_line_ids:
            raise ValidationError(
                _("Please Select Atleast One Table In The Productor Residue."))
        for value in productor_residue.lot_attribute_line_ids:
            for tab in value.value_ids:
                split_value = tab.name.split(" ")
                productor_table_list.append(split_value[0])
            productor_all_table = '//'.join(productor_table_list)
        gestor_table_list = []
        if not gestor_residue.lot_attribute_line_ids:
            raise ValidationError(
                _("Please Select Atleast One Table In The Gestor Residue."))
        for value in gestor_residue.lot_attribute_line_ids:
            for tab in value.value_ids:
                split_value = tab.name.split(" ")
                gestor_table_list.append(split_value[0])
            gestor_all_table = '//'.join(gestor_table_list)
        data = {
            "documento": {
                "actualizar_datos": 'S',
                "consecuencias_legales": self.consecuencias_legales,
                "residuo_productor":
                {
                    "tablas": productor_all_table,
                    "ler": productor_residue.lercode_id.name,
                    "peso": productor_residue.weight,
                },
                "residuo_gestor":
                {
                    "tablas": gestor_all_table,
                    "ler": gestor_residue.lercode_id.name,
                    "peso": gestor_residue.weight,
                },
                "datos_admision":
                {
                    "admision": self.data_admission and 'S' or 'N',
                    "parametros_admision": self.parametros_admision
                },
                "gestor":
                {
                    "nombre": self.gestor_center_id.parent_id.name,
                    "codigo_externo": self.gestor_center_id.parent_id.external_code,
                    "cif_nif_nie": self.gestor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.gestor_center_id.parent_id.business_name,
                    "apellido1": self.gestor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.gestor_center_id.authorization_code_id and self.gestor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.gestor_center_id.parent_id.association_type_id and self.gestor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.gestor_center_id.phone,
                            "nombre": self.gestor_center_id.name,
                            "nima": self.gestor_center_id.nima,
                            "codigo_municipio": self.gestor_center_id.municipality_code_id and self.gestor_center_id.municipality_code_id.code,
                            "direccion": self.gestor_center_id.street,
                            "email": self.gestor_center_id.email,
                            "codigo_via": self.gestor_center_id.code_via_id and self.gestor_center_id.code_via_id.code,
                            "codigo_postal": self.gestor_center_id.zip,
                            "autorizacion": self.gestor_center_id.authorization_code
                        },
                },
                "productor":
                {
                    "nombre": self.productor_center_id.parent_id.name,
                    "cif_nif_nie": self.productor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.productor_center_id.parent_id.business_name,
                    "apellido1": self.productor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.productor_center_id.authorization_code_id and self.productor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.productor_center_id.parent_id.association_type_id and self.productor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.productor_center_id.phone,
                            "localidad": self.productor_center_id.city,
                            "nombre": self.productor_center_id.name,
                            "nima": self.productor_center_id.nima,
                            "codigo_municipio": self.productor_center_id.municipality_code_id and self.productor_center_id.municipality_code_id.code,
                            "direccion": self.productor_center_id.street,
                            "email": self.productor_center_id.email,
                            "codigo_via": self.productor_center_id.code_via_id and self.productor_center_id.code_via_id.code,
                            "codigo_postal": self.productor_center_id.zip,
                            "autorizacion": self.productor_center_id.authorization_code
                        },
                },
            },
        }
        if self.explotador_gestor_center_id:
            data['documento'].update({
                "                explotador_gestor":
                {
                    "nombre": self.explotador_gestor_center_id.parent_id.name,
                    "codigo_externo": self.explotador_gestor_center_id.parent_id.external_code,
                    "cif_nif_nie": self.explotador_gestor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.explotador_gestor_center_id.parent_id.business_name,
                    "apellido1": self.explotador_gestor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.explotador_gestor_center_id.authorization_code_id and self.explotador_gestor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.explotador_gestor_center_id.parent_id.association_type_id and self.explotador_gestor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.explotador_gestor_center_id.phone,
                            "localidad": self.explotador_gestor_center_id.city,
                            "nombre": self.explotador_gestor_center_id.name,
                            "nima": self.explotador_gestor_center_id.nima,
                            "codigo_municipio": self.explotador_gestor_center_id.municipality_code_id and self.explotador_gestor_center_id.municipality_code_id.code,
                            "direccion": self.explotador_gestor_center_id.street,
                            "email": self.explotador_gestor_center_id.email,
                            "codigo_via": self.explotador_gestor_center_id.code_via_id and self.explotador_gestor_center_id.code_via_id.code,
                            "codigo_postal": self.explotador_gestor_center_id.zip,
                            "autorizacion": self.explotador_gestor_center_id.authorization_code
                        },
                }})
        if self.explotador_productor_center_id:
            data['documento'].update({
                "explotador_productor":
                {
                    "nombre": self.explotador_productor_center_id.parent_id.name,
                    "codigo_externo": self.explotador_productor_center_id.parent_id.external_code,
                    "cif_nif_nie": self.explotador_productor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.explotador_productor_center_id.parent_id.business_name,
                    "apellido1": self.explotador_productor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.explotador_productor_center_id.authorization_code_id and self.explotador_productor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.explotador_productor_center_id.parent_id.association_type_id and self.explotador_productor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.explotador_productor_center_id.phone,
                            "localidad": self.explotador_productor_center_id.city,
                            "nombre": self.explotador_productor_center_id.name,
                            "nima": self.explotador_productor_center_id.nima,
                            "codigo_municipio": self.explotador_productor_center_id.municipality_code_id and self.explotador_productor_center_id.municipality_code_id.code,
                            "direccion": self.explotador_productor_center_id.street,
                            "email": self.explotador_productor_center_id.email,
                            "codigo_via": self.explotador_productor_center_id.code_via_id and self.explotador_productor_center_id.code_via_id.code,
                            "codigo_postal": self.explotador_productor_center_id.zip,
                            "autorizacion": self.explotador_productor_center_id.authorization_code
                        },
                }})
        if self.operador_center_id:
            data['documento'].update({
                "operador":
                    {
                        "nombre": self.operator_center_id.parent_id.name,
                        "codigo_externo": self.operator_center_id.parent_id.external_code,
                        "cif_nif_nie": self.operator_center_id.parent_id.cif_nif_nie,
                        "razon_social": self.operator_center_id.parent_id.business_name,
                        "apellido1": self.operator_center_id.parent_id.lastname_1,
                        "codigo_tipo_entidad": self.operator_center_id.authorization_code_id and self.operator_center_id.authorization_code_id.code,
                        "codigo_tipo_asociacion": self.operator_center_id.parent_id.association_type_id and self.operator_center_id.parent_id.association_type_id.code,
                        "centro":
                        {
                            "telefono": self.operator_center_id.phone,
                            "localidad": self.operator_center_id.city,
                            "nombre": self.operator_center_id.name,
                            "nima": self.operator_center_id.nima,
                            "codigo_municipio": self.operator_center_id.municipality_code_id and self.operator_center_id.municipality_code_id.code,
                            "direccion": self.operator_center_id.street,
                            "email": self.operator_center_id.email,
                            "codigo_via": self.operator_center_id.code_via_id and self.operator_center_id.code_via_id.code,
                            "codigo_postal": self.operator_center_id.zip,
                            "autorizacion": self.operator_center_id.authorization_code
                        },
                    },
            })
        if self.codigo:
            data['documento'].update({'codigo': self.codigo})
        return data

    def create_di(self):
        teixo_user_name = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_user', default='')
        teixo_token = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_token', default='')
        api_url = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_url', default='')

        data = self.create_di_data()
        full_api = api_url + '/di/'
        headers = {'content-type': 'application/json; charset=utf-8',
                   'Accept': 'application/json'}
        auth = HTTPBasicAuth(str(teixo_user_name), str(teixo_token))
        login_response = requests.post(
            full_api, data=json.dumps(data), headers=headers, auth=auth)
        if login_response.__dict__.get('status_code') == 201:
            if '_content' in login_response.__dict__:
                convert_data = login_response.__dict__.get(
                    '_content').decode('utf-8')
                get_data = ast.literal_eval(convert_data)
                if 'codigo' in get_data:
                    self.codigo = get_data.get('codigo') or ''
                if 'url_pdf' in get_data:
                    self.teixo_doc_url = get_data.get('url_pdf') or ''
        else:
            raise UserError(_('%s') % (login_response.text))

    def create_di_data(self):
        productor_residue = self.productor_residue_id
        gestor_residue = self.gestor_residue_id
        if not productor_residue or not gestor_residue:
            raise ValidationError(
                _("Please Select Productor Residue and Gestor Residue For Create CT."))
        productor_table_list = []
        if not productor_residue.lot_attribute_line_ids:
            raise ValidationError(
                _("Please Select At least One Table In The Productor Residue."))
        for value in productor_residue.lot_attribute_line_ids:
            for tab in value.value_ids:
                split_value = tab.name.split(" ")
                productor_table_list.append(split_value[0])
            productor_all_table = '//'.join(productor_table_list)
        gestor_table_list = []
        if not gestor_residue.lot_attribute_line_ids:
            raise ValidationError(
                _("Please Select At least One Table In The Gestor Residue."))
        if not self.transportista_center_id.parent_id.vehicle_ids:
            raise ValidationError(
                _("There is no vehicle available for this transportista ,Please create one."))
        for value in gestor_residue.lot_attribute_line_ids:
            for tab in value.value_ids:
                split_value = tab.name.split(" ")
                gestor_table_list.append(split_value[0])
            gestor_all_table = '//'.join(gestor_table_list)
        data = {
            "documento": {
                "estado": self.state_di,
                "actualizar_datos": 'S',
                "fecha_inicio_traslado": self.start_date_di,
                "residuo_productor":
                {
                    "tablas": productor_all_table,
                    "ler": productor_residue.lercode_id.name,
                    "peso_bruto": self.gross_weight_residue,
                    "peso_neto": self.net_weight_residue
                },
                "residuo_gestor":
                {
                    "tablas": gestor_all_table,
                    "ler": gestor_residue.lercode_id.name,
                    "peso_bruto": self.gross_weight_residue,
                    "peso_neto": self.net_weight_residue
                },
                "gestor":
                {
                    "nombre": self.gestor_center_id.parent_id.name,
                    "codigo_externo": self.gestor_center_id.parent_id.external_code,
                    "cif_nif_nie": self.gestor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.gestor_center_id.parent_id.business_name,
                    "apellido1": self.gestor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.gestor_center_id.authorization_code_id and self.gestor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.gestor_center_id.parent_id.association_type_id and self.gestor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.gestor_center_id.phone,
                            "nombre": self.gestor_center_id.name,
                            "nima": self.gestor_center_id.nima,
                            "codigo_municipio": self.gestor_center_id.municipality_code_id and self.gestor_center_id.municipality_code_id.code,
                            "direccion": self.gestor_center_id.street,
                            "email": self.gestor_center_id.email,
                            "codigo_via": self.gestor_center_id.code_via_id and self.gestor_center_id.code_via_id.code,
                            "codigo_postal": self.gestor_center_id.zip,
                            "autorizacion": self.gestor_center_id.authorization_code
                        },
                },
                "productor":
                {
                    "nombre": self.productor_center_id.parent_id.name,
                    "codigo_externo": self.productor_center_id.parent_id.external_code,
                    "cif_nif_nie": self.productor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.productor_center_id.parent_id.business_name,
                    "apellido1": self.productor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.productor_center_id.authorization_code_id and self.productor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.productor_center_id.parent_id.association_type_id and self.productor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.productor_center_id.phone,
                            "localidad": self.productor_center_id.city,
                            "nombre": self.productor_center_id.name,
                            "nima": self.productor_center_id.nima,
                            "codigo_municipio": self.productor_center_id.municipality_code_id and self.productor_center_id.municipality_code_id.code,
                            "direccion": self.productor_center_id.street,
                            "email": self.productor_center_id.email,
                            "codigo_via": self.productor_center_id.code_via_id and self.productor_center_id.code_via_id.code,
                            "codigo_postal": self.productor_center_id.zip,
                            "autorizacion": self.productor_center_id.authorization_code
                        },
                },
                "transportista":
                {
                    "nombre": self.transportista_center_id.parent_id.name,
                    "codigo_externo": self.transportista_center_id.parent_id.external_code,
                    "codigo_tipo_transporte": self.transportista_center_id.parent_id.transport_type_id and self.transportista_center_id.parent_id.transport_type_id.code,
                    "cif_nif_nie": self.transportista_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.transportista_center_id.parent_id.business_name,
                    "apellido1": self.transportista_center_id.parent_id.lastname_1,
                    "matricula": self.transportista_center_id.parent_id.vehicle_ids and self.transportista_center_id.parent_id.vehicle_ids[0].license_plate,
                    "codigo_tipo_entidad": self.transportista_center_id.parent_id.authorization_code_id and self.transportista_center_id.parent_id.authorization_code_id.code,
                        "codigo_tipo_asociacion": self.transportista_center_id.parent_id.association_type_id and self.transportista_center_id.parent_id.association_type_id.code,
                        "codigo_forma_transporte": self.transportista_center_id.parent_id.transportaion_form_id and self.transportista_center_id.parent_id.transportaion_form_id.code,
                        "centro":
                        {
                            "telefono": self.transportista_center_id.phone,
                            "nombre": self.transportista_center_id.name,
                            "nima": self.transportista_center_id.nima,
                            "codigo_municipio": self.transportista_center_id.municipality_code_id and self.transportista_center_id.municipality_code_id.code,
                            "direccion": self.transportista_center_id.street,
                            "email": self.transportista_center_id.email,
                            "codigo_via": self.transportista_center_id.code_via_id and self.transportista_center_id.code_via_id.code,
                            "codigo_postal": self.transportista_center_id.zip,
                            "autorizacion": self.transportista_center_id.authorization_code
                    },
                }
            },
        }
        if self.acceptance_id:
            data['documento'].update({
                "aceptacion":
                    {
                        "codigo_aceptacion": self.acceptance_id.code,
                        "cantidad_real": self.real_qty,
                        "fecha": self.acceptance_date,
                    },
            })
        if self.incedence_id_1:
            data['documento'].update({
                "incidencia_1": {
                    "codigo_incidencia": self.incedence_id_1.code,
                    "observaciones": self.incedence1_observation
                },
            })
        if self.incedence_id_2:
            data['documento'].update({
                "incidencia_2": {
                    "codigo_incidencia": self.incedence_id_2.code,
                    "observaciones": self.incedence1_observation
                },
            })
        if self.ct_id:
            data['documento'].update({'codigo_da': self.ct_id.codigo})
        if self.nt_id:
            data['documento'].update({'codigo_nt': self.nt_id.codigo})
        if self.codigo:
            data['documento'].update({'codigo': self.codigo})
        if self.explotador_gestor_center_id:
            data['documento'].update({
                "                explotador_gestor":
                {
                    "nombre": self.explotador_gestor_center_id.parent_id.name,
                    "codigo_externo": self.explotador_gestor_center_id.parent_id.external_code,
                    "cif_nif_nie": self.explotador_gestor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.explotador_gestor_center_id.parent_id.business_name,
                    "apellido1": self.explotador_gestor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.explotador_gestor_center_id.authorization_code_id and self.explotador_gestor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.explotador_gestor_center_id.parent_id.association_type_id and self.explotador_gestor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.explotador_gestor_center_id.phone,
                            "localidad": self.explotador_gestor_center_id.city,
                            "nombre": self.explotador_gestor_center_id.name,
                            "nima": self.explotador_gestor_center_id.nima,
                            "codigo_municipio": self.explotador_gestor_center_id.municipality_code_id and self.explotador_gestor_center_id.municipality_code_id.code,
                            "direccion": self.explotador_gestor_center_id.street,
                            "email": self.explotador_gestor_center_id.email,
                            "codigo_via": self.explotador_gestor_center_id.code_via_id and self.explotador_gestor_center_id.code_via_id.code,
                            "codigo_postal": self.explotador_gestor_center_id.zip,
                            "autorizacion": self.explotador_gestor_center_id.authorization_code
                        },
                }})
        if self.explotador_productor_center_id:
            data['documento'].update({
                "explotador_productor":
                {
                    "nombre": self.explotador_productor_center_id.parent_id.name,
                    "codigo_externo": self.explotador_productor_center_id.parent_id.external_code,
                    "cif_nif_nie": self.explotador_productor_center_id.parent_id.cif_nif_nie,
                    "razon_social": self.explotador_productor_center_id.parent_id.business_name,
                    "apellido1": self.explotador_productor_center_id.parent_id.lastname_1,
                    "codigo_tipo_entidad": self.explotador_productor_center_id.authorization_code_id and self.explotador_productor_center_id.authorization_code_id.code,
                    "codigo_tipo_asociacion": self.explotador_productor_center_id.parent_id.association_type_id and self.explotador_productor_center_id.parent_id.association_type_id.code,
                    "centro":
                        {
                            "telefono": self.explotador_productor_center_id.phone,
                            "localidad": self.explotador_productor_center_id.city,
                            "nombre": self.explotador_productor_center_id.name,
                            "nima": self.explotador_productor_center_id.nima,
                            "codigo_municipio": self.explotador_productor_center_id.municipality_code_id and self.explotador_productor_center_id.municipality_code_id.code,
                            "direccion": self.explotador_productor_center_id.street,
                            "email": self.explotador_productor_center_id.email,
                            "codigo_via": self.explotador_productor_center_id.code_via_id and self.explotador_productor_center_id.code_via_id.code,
                            "codigo_postal": self.explotador_productor_center_id.zip,
                            "autorizacion": self.explotador_productor_center_id.authorization_code
                        },
                }})
        if self.operador_center_id:
            data['documento'].update({
                "operador":
                    {
                        "nombre": self.operator_center_id.parent_id.name,
                        "codigo_externo": self.operator_center_id.parent_id.external_code,
                        "cif_nif_nie": self.operator_center_id.parent_id.cif_nif_nie,
                        "razon_social": self.operator_center_id.parent_id.business_name,
                        "apellido1": self.operator_center_id.parent_id.lastname_1,
                        "codigo_tipo_entidad": self.operator_center_id.authorization_code_id and self.operator_center_id.authorization_code_id.code,
                        "codigo_tipo_asociacion": self.operator_center_id.parent_id.association_type_id and self.operator_center_id.parent_id.association_type_id.code,
                        "centro":
                        {
                            "telefono": self.operator_center_id.phone,
                            "localidad": self.operator_center_id.city,
                            "nombre": self.operator_center_id.name,
                            "nima": self.operator_center_id.nima,
                            "codigo_municipio": self.operator_center_id.municipality_code_id and self.operator_center_id.municipality_code_id.code,
                            "direccion": self.operator_center_id.street,
                            "email": self.operator_center_id.email,
                            "codigo_via": self.operator_center_id.code_via_id and self.operator_center_id.code_via_id.code,
                            "codigo_postal": self.operator_center_id.zip,
                            "autorizacion": self.operator_center_id.authorization_code
                        },
                    },
            })
        return data

    def send_to_admin_data(self):
        data = {
            "enviar_admon": 'S',
            "documento": {
                'codigo': self.codigo
            }
        }
        self.enviar_admon = 1
        return data

    def send_to_admin(self):
        teixo_user_name = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_user', default='')
        teixo_token = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_token', default='')
        api_url = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_url', default='')

        data = self.send_to_admin_data()
        if self.doc_type == 'di':
            full_api = api_url + '/di/send_di'
        elif self.doc_type == 'nt':
            full_api = api_url + '/nt/send_nt'
        elif self.doc_type == 'ct':
            full_api = api_url + '/ct/send_ct'
        headers = {'content-type': 'application/json; charset=utf-8',
                   'Accept': 'application/json'}
        auth = HTTPBasicAuth(str(teixo_user_name), str(teixo_token))
        login_response = requests.post(
            full_api, data=json.dumps(data), headers=headers, auth=auth)
        if login_response.__dict__.get('status_code') == 200:
            if '_content' in login_response.__dict__:
                convert_data = login_response.__dict__.get(
                    '_content').decode('utf-8')
                get_data = ast.literal_eval(convert_data)
                if 'estado_admon' in get_data:
                    self.estado_admon = get_data.get('estado_admon')
                if 'error_envio_admon' in get_data:
                    self.error_envio_admon = get_data.get(
                        'error_envio_admon') or ''
                if 'url_pdf' in get_data:
                    self.teixo_doc_url = get_data.get('url_pdf') or ''
        else:
            raise UserError(_('%s') % (login_response.text))

    def check_with_administration(self):
        teixo_user_name = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_user', default='')
        teixo_token = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_token', default='')
        api_url = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_url', default='')

        if self.doc_type == 'di':
            full_api = api_url + '/di/' + self.codigo
        elif self.doc_type == 'nt':
            full_api = api_url + '/nt/' + self.codigo
        elif self.doc_type == 'ct':
            full_api = api_url + '/ct/' + self.codigo
        headers = {'content-type': 'application/json; charset=utf-8',
                   'Accept': 'application/json'}
        auth = HTTPBasicAuth(str(teixo_user_name), str(teixo_token))
        login_response = requests.get(full_api, headers=headers, auth=auth)
        if login_response.__dict__.get('status_code') == 200:
            if '_content' in login_response.__dict__:
                convert_data = login_response.__dict__.get(
                    '_content').decode('utf-8')
                get_data = ast.literal_eval(convert_data)
                if 'estado_admon' in get_data:
                    self.estado_admon = get_data.get('estado_admon') or ''
                if 'url_pdf' in get_data:
                    self.teixo_doc_url = get_data.get('url_pdf') or ''
                if 'error_envio_admon' in get_data:
                    self.error_envio_admon = get_data.get(
                        'error_envio_admon') or ''
        else:
            raise UserError(_('%s') % (login_response.text))

    def doc_annul(self):
        teixo_user_name = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_user', default='')
        teixo_token = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_token', default='')
        api_url = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_url', default='')

        if self.doc_type == 'di':
            full_api = api_url + '/di/' + self.codigo
        elif self.doc_type == 'nt':
            full_api = api_url + '/nt/' + self.codigo
        elif self.doc_type == 'ct':
            full_api = api_url + '/ct/' + self.codigo
        headers = {'content-type': 'application/json; charset=utf-8',
                   'Accept': 'application/json'}
        auth = HTTPBasicAuth(str(teixo_user_name), str(teixo_token))
        login_response = requests.delete(
            full_api, headers=headers, auth=auth)
        if login_response.__dict__.get('status_code') == 200:
            pass
        else:
            raise UserError(_('%s') % (login_response.text))


class ResAcceptanceCode(models.Model):
    """Acceptance Code"""
    _name = "res.acceptance"
    _rec_name = "code"

    code = fields.Char(string="Code", required=True)
    description = fields.Char(string="Description", required=True)

    @api.multi
    def name_get(self):
        data = []
        for rec in self:
            display_value = rec.code
            display_value += ('-' + str(rec.description)) or ""
            data.append((rec.id, display_value))
        return data


class ResIncidence(models.Model):
    """Incidence Code"""
    _name = "res.incidence"
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
