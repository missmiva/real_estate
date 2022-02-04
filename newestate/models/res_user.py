from odoo import api,models,fields

class ResUser(models.Model):
    _inherit = "res.users"

    property_id = fields.One2many('estate.properties', 'salesman_id')
    is_buyer=fields.Boolean()