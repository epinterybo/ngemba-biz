from odoo import fields, models


class CwProduct(models.Model):
    _name = 'cw.old.product'
    _description = 'CW old Product Data'
    
    display_name = fields.Char(string="Product Name", required=False) 
    x_cw_product_list_id = fields.Char(string="Product ListID", required=True)
    description = fields.Text(string="Product Description", required=False)
    
    