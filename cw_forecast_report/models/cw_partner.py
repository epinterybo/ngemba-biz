from odoo import models, fields

class CwCustomer(models.Model):
    _name = "cw.old.partner"
    _description = "CW Old Partner"
    
    name = fields.Char(string="Name(s)", required=False)
    is_seller = fields.Boolean(string="Is Seller", default=False)
    x_cw_list_id = fields.Char(string="ListID", required=True)
    description = fields.Text(string="Note about User", required=False)
    