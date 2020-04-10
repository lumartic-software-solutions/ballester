from odoo import api, fields, models, _
# coding=utf-8


class ResCenterCnae(models.Model):
    _name = 'res.center.cnae'
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


class ResEntityType(models.Model):
    """Entity"""
    _name = "res.entity.type"
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

class AuthorizationCode(models.Model):
    _name = 'authorization.code'
    _rec_name = "code"

    code = fields.Char(string="Code", required=True)
    partner_id = fields.Many2one("res.partner", readonly=True, string='Related Contact')
    entity_type_id = fields.Many2one("res.entity.type", required=True, string='código tipo entidad')


    @api.multi
    def name_get(self):
        data = []
        for rec in self:
            display_value = rec.code
            display_value += ('-' + rec.entity_type_id.code) or ""
            data.append((rec.id, display_value))
        return data

class ResMunicipio(models.Model):
    """Municipio"""
    _name = "res.municipio"
    _rec_name = "code"

    code = fields.Char(string="Code", required=True)
    description = fields.Char(string="Description", required=True)
    state_id = fields.Many2one('res.country.state', string="Province", required=True)

    @api.multi
    def name_get(self):
        data = []
        for rec in self:
            display_value = rec.code
            display_value += ('-' + rec.description) or ""
            data.append((rec.id, display_value))
        return data


class ResCodeVia(models.Model):
    """CodeVia"""
    _name = "res.codevia"
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
    
class ResResidueCenter(models.Model):
    """Residue Center"""
    _name = "res.residue.center"

    product_id = fields.Many2one('product.template', string="Residue", required=True)
    center_id = fields.Many2one("res.partner", required=True, string="Center", domain=[('type', '=', 'center')])
    partner_id = fields.Many2one("res.partner", required=True, string="Partner")
