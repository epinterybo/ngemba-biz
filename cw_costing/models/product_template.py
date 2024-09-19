from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    cw_harmonized_code_id = fields.Many2one('cw.costing.harmonized.code', string="Harmonized Code")
    
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    def cw_search_harmonized_code_id(self):
        res = self.env['cw.costing.harmonized.code']
        if self:
            self.ensure_one()
            if self.cw_harmonized_code_id:
                res = self.cw_harmonized_code_id
            elif self.categ_id:
                res = self.categ_id.cw_search_harmonized_code_id()
        return res
    
    