from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    x_cw_bonus_is_special_category = fields.Boolean(string="Is special Category", default=False)
    x_cw_bonus_point_for_category = fields.Integer(string="Bonus point for category", default=0)
    
    
    def get_bonus_point_for_category(self):
        self.ensure_one()
        if self.x_cw_bonus_point_for_category and self.x_cw_bonus_point_for_category > 0:
            return self.x_cw_bonus_point_for_category
        elif self.parent_id:
            for category in self:
                if category.x_cw_bonus_point_for_category and category.x_cw_bonus_point_for_category:
                    return category.x_cw_bonus_point_for_category
        return 0