from odoo import fields, models, api


class LeasePropertyestate(models.Model):
    _name ="lease.estate.property"
    _inherits ={'estate.properties':'lease_id'}

    lease_id = fields.Many2one('estate.properties')
    lease_duration = fields.Float()
    lease_rent = fields.Float()
    prise = fields.Float()
    lease_date = fields.Date()

class Lease(models.Model):
    _name ="lease"
    _inherit ="lease.estate.property"

    internal_lease=fields.Text()

   