from odoo import models, fields, _, api
from odoo.exceptions import ValidationError, UserError
from requests.auth import HTTPBasicAuth
import ast
import requests
import json


class ChangeDiStateWizard(models.TransientModel):
    _name = 'change.state.wizard'

    document_id = fields.Many2one('document.teixo', "Document")
    updated_state = fields.Selection([('pendiente_aceptacion', 'Pendiente Aceptacion'), (
        'cerrado', 'Cerrado')], string="Updated State", required=True)
    gross_weight_residue = fields.Float("Residuo Peso Bruto", required=True)
    net_weight_residue = fields.Float("Residuo Peso Neto", required=True)

    @api.model
    def default_get(self, vals):
        res = super(ChangeDiStateWizard, self).default_get(vals)
        context = self._context
        teixo = self.env['document.teixo'].browse(context['active_id'])
        res.update({'document_id': context['active_id'],
                    'gross_weight_residue': teixo.gross_weight_residue,
                    'net_weight_residue': teixo.net_weight_residue})
        return res

    def change_di_state(self):
        teixo_user_name = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_user', default='')
        teixo_token = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_token', default='')
        api_url = self.env['ir.config_parameter'].sudo(
        ).get_param('teixo_url', default='')

        data = self.change_di_state_data()
        full_api = api_url + '/di/' + \
            str(self.document_id.codigo)
        headers = {'content-type': 'application/json; charset=utf-8',
                   'Accept': 'application/json'}
        auth = HTTPBasicAuth(str(teixo_user_name), str(teixo_token))
        login_response = requests.put(
            full_api, data=json.dumps(data), headers=headers, auth=auth)
        if login_response.__dict__.get('status_code') == 200:
            if '_content' in login_response.__dict__:
                convert_data = login_response.__dict__.get(
                    '_content').decode('utf-8')
                get_data = ast.literal_eval(convert_data)
                if 'url_pdf' in get_data:
                    self.document_id.teixo_doc_url = get_data.get(
                        'url_pdf') or ''
                    self.document_id.state = self.updated_state
        else:
            raise UserError(_('%s') % (login_response.text))
        self.document_id.state_di = self.updated_state
        return {'type': 'ir.actions.act_window_close'}

    def change_di_state_data(self):
        data = {
            "documento": {
                "fecha_inicio_traslado": self.document_id.start_date_di,
                "codigo": self.document_id.codigo,
                "estado": self.updated_state,
                "residuo":
                {
                    "peso_bruto": self.gross_weight_residue,
                    "peso_neto": self.net_weight_residue
                },
                "transportista": {
                    "matricula": self.document_id.transportista_center_id.parent_id.vehicle_ids and self.document_id.transportista_center_id.parent_id.vehicle_ids[0].license_plate,
                    "codigo_forma_transporte": self.document_id.transportista_center_id.parent_id.transportaion_form_id and self.document_id.transportista_center_id.parent_id.transportaion_form_id.code,
                }
            },
        }
        acceptance_dict = {}
        if self.document_id.real_qty:
            acceptance_dict.update(
                {"cantidad_real": self.document_id.real_qty})

        if self.document_id.acceptance_id:
            acceptance_dict.update(
                {"codigo_aceptacion": self.document_id.acceptance_id.code})

        if self.document_id.acceptance_date:
            acceptance_dict.update({"fecha": self.document_id.acceptance_date})
        if self.document_id.incedence_id_1:
            acceptance_dict.update({
                "incidencia_1": {
                    "codigo_incidencia": self.document_id.incedence_id_1.code,
                    "observaciones": self.document_id.incedence1_observation
                },
            })
        if self.document_id.incedence_id_2:
            acceptance_dict.update({
                "incidencia_2": {
                    "codigo_incidencia": self.document_id.incedence_id_2.code,
                    "observaciones": self.document_id.incedence2_observation
                },
            })

        data['documento'].update({
            "aceptacion": acceptance_dict,
        })
        return data
