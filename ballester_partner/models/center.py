# coding=utf-8
from odoo import api, fields, models, _



class ResCenter(models.Model):
    _name = 'res.center'
    _rec_name = 'first_name'

    partner_id = fields.Many2one('res.partner', string="Contact")
    authorization = fields.Char(string="Authorization", required=True)
    external_code = fields.Char(string="External Code")
    municipality_code_id = fields.Many2one('res.municipio', string="Municipality Code", required=True)
    postal_code = fields.Char(string="Postal Code", required=True)
    code_via_id = fields.Many2one('res.codevia', string="Code Via", required=True)
    address = fields.Text(string="Address", required=True)
    email = fields.Char(string="E-mail", required=True)
    location = fields.Char(string="Location", required=True)
    nima = fields.Char(string="Nima", required=True)
    first_name = fields.Char(string="First Name", required=True)
    phone = fields.Char(string="Phone", required=True)
    cnae_id = fields.Many2one('res.center.cnae', string="CNAE")


class ResCenterCnae(models.Model):
    _name = 'res.center.cnae'

    name = fields.Char(string="Nombre", required=True)


class ResCenterMunicipio(models.Model):
    """Municipio"""
    _name = "res.municipio"

    code = fields.Char(string="Code")
    description = fields.Char(string="Description")
    state_id = fields.Many2one('res.country.state', string="Province")

    @api.multi
    def name_get(self):
        data = []
        for rec in self:
            display_value = rec.code
            display_value += ('-' + str(rec.description)) or ""
            data.append((rec.id, display_value))
            return data


class ResCenterCodeVia(models.Model):
    """CodeVia"""
    _name = "res.codevia"

    code = fields.Char(string="Code")
    description = fields.Char(string="Description")

    @api.multi
    def name_get(self):
        data = []
        for rec in self:
            display_value = rec.code
            display_value += ('-' + str(rec.description)) or ""
            data.append((rec.id, display_value))
            return data
