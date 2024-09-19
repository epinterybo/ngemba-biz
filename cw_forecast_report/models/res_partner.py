from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_cw_list_id = fields.Char(string="ListID", required=False)
    
    
    @api.model
    def check_and_update_list_id(self):
        records = self.search([
            ('x_cw_list_id', '=', False)
        ])
        
        for record in records:
            if record.x_studio_cw_listid:
                record.write({
                    'x_cw_list_id': record.x_studio_cw_listid
                })