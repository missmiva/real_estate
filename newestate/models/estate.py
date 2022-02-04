from odoo import fields, models, api
from odoo.exceptions import UserError


class estate_property(models.Model):
    _name = "estate.properties"
    _description = "estate property"

    def _get_description(self):
        if self.env.context.get('is_my_property'):
            return self.env.user.name + "'s MY Property"

    name = fields.Char(default="Unknown")
    selling_price = fields.Float()
    bedrom = fields.Integer(default=2)
    postcode = fields.Char()
    image = fields.Image()
    date_availability = fields.Date(copy=False)
    expected_price = fields.Float(help="help")
    living_area = fields.Integer()
    garden_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    active = fields.Boolean(default=True)
    description = fields.Text(default=_get_description)
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ])
    property_type_id = fields.Many2one('property.type')
    property_tag_id = fields.Many2many('estate.tag')
    property_offer_id = fields.One2many('estate.offer','property_id')
    offer_ids = fields.One2many('estate.offer', 'property_id', 'property.type"')
    total_area = fields.Integer(compute="_total_area", inverse="_inverse_area",search="_search_area")
    best_offer = fields.Float(compute="_best_prize")
    partner_id = fields.Many2one('res.partner')
    current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user , readonly=True)
    salesman_id = fields.Many2one('res.users',default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner')
    state = fields.Selection([('new', 'New'), ('sold', 'Sold'), ('cancel', 'Cancelled')], default='new')
    #partner_ids = fields.Many2o('res.partner')
    #p_name = fields.Char(related='offer_ids.partner_id.name', string="OFFER NAME")
   # partner = fields.Char(related='partner_ids.partner_id.name', string="partner")

 
    def _search_area(self, operator, value):
        self.env.cr.execute(
            "SELECT id from estate.properties where total_area::%s %s" % (operator, value))
        ids = self.env.cr.fetchall()
        return [('id', 'in', [id[0] for id in ids])]
    
    def action_sold(self):
        # print("\n\n In action sold")
        for record in self:
            if record.state == 'cancel':
                raise UserError("Cancel Property cannot be sold")
            record.state = 'sold'
            # return some action

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Sold Property cannot be canceled")
            record.state = 'cancel'

    
    def open_offers(self):
        view_id = self.env.ref('newestate.estate_property_offer_tree').id
        return {
            "name": "Offers",
            "type": "ir.actions.act_window",
            "res_model": "estate.offer",
            "views": [[view_id, 'tree']],
            "target": "new",
            "domain": [('property_id', '=', self.id)]
        }
    def confirm_offers(self):
        view_id = self.env.ref('newestate.estate_property_offer_tree').id
        return {
            "name": "Offers",
            "type": "ir.actions.act_window",
            "res_model": "estate.offer",
            "views": [[view_id, 'tree']],
            "target": "new",
            "domain": [('status', '=', 'accepted')]
        }

    @api.onchange('garden')
    def _onchange_garden(self):
        for record in self:
            if record.garden:
                record.garden_area = 10
                record.garden_orientation = 'west'
            else:
                record.garden_area = 0
                record.garden_orientation = None

    @api.depends('offer_ids.price')
    def _best_prize(self):
        for record in self:
            max_price = 0
            for offer in record.offer_ids:
                if offer.price > max_price:
                    max_price = offer.price
            record.best_offer = max_price

    @api.depends('garden_area', 'living_area')
    def _total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    def _inverse_area(self):
        for record in self:
            record.living_area = record.garden_area = record.total_area / 2

    @api.constrains('garden_area', 'living_area')
    def _check_garden_area(self):
        for record in self:
            if record.living_area > record.garden_area:
                raise UserError("garden area must be bigger than living area")

    @api.constrains('expected_price')
    def _expectedprize(self):
        for record in self:
            if record.expected_price == 0:
                raise UserError("expected prize is not null")

# class Leased_property(models.Model):
#     _name ="lease.property"
#     _inherits ={'estate.properties':'lease_id'}

#     lease_id = fields.Many2one('estate.properties')
#     lease_duration = fields.Float()
#     lease_rent = fields.Float()
#     prise = fields.Float()
#     lease_date = fields.Date()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    buyer_property_id = fields.One2many('estate.properties', 'buyer_id')
    is_buyer = fields.Boolean()

    offer_ids = fields.One2many('estate.offer', 'partner_id')


class estate_property_type(models.Model):
    _name = "property.type"
    _description = "estate property type"

    name = fields.Char()
    property_ids = fields.One2many('estate.properties', 'property_type_id')
    offers = fields.One2many('estate.offer', 'property_type_id')

class Extended_property_type(models.Model):
    _name = "newproperty.type"
    _inherit = "property.type"

    internal_property=fields.Text()

class Extended_property_type(models.Model):
   
    _inherit = "property.type"

    internal_property=fields.Text()
    external_property=fields.Text()

class garden_estate_property_type(models.Model):
    _name = "garden.property.type"
    _description = "estate property type"

    name = fields.Char()
    property_ids = fields.One2many('estate.properties', 'property_type_id')
    offers = fields.One2many('estate.offer', 'property_type_id')
    partner_id = fields.Many2one('res.partner')


class estate_tag(models.Model):
    _name = 'estate.tag'
    _description = 'estate property tag'

    name = fields.Char()
    color = fields.Integer()


class estate_offer(models.Model):
    _name = 'estate.offer'
    _description = 'estate offer'

    name = fields.Char()
    price = fields.Float()
    status = fields.Selection(
        [('accepted', 'Accepted'), ('rejected', 'Rejected')])
    partner_id = fields.Many2one('res.partner')
    property_id = fields.Many2one('estate.properties')
    property_type_id = fields.Many2one(related='property_id.property_type_id')

    def action_accepted(self):
        for record in self:
            record.status = "accepted"

    def action_rejected(self):
        for record in self:
            record.status = "rejected"

# class Buyer_partner(models.Model):

#     _inherit = 'res.partner'

#     is_buyer = fields.Boolean(domain="[('is_buyer', '=', ['True'])]")


