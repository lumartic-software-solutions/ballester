from odoo import api, fields, models, _


class ProductProduct(models.Model):
    """Product"""
    _inherit = "product.product"

    center_id = fields.Many2one('res.center', string="Residue Center")
