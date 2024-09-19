from odoo import api, fields, models

class CwHarmonizedCode(models.Model):
    _name = 'cw.costing.harmonized.code'
    _description = 'CW Costing Harmonized Code'
    
    name = fields.Char('HS Code', required=True)
    com_value = fields.Float('COM', required=True, default=0.0, help="Cost of Manufacture (fixed amount per hs code)")
    exm_value = fields.Float('EXM', required=True, default=0.0, help="Export Market Value (fixed amount per hs code)")
    cid_rate = fields.Float('CID', required=True, default=0.0, help="Customs Import Duty Rate")
    warranty_rate = fields.Float(string='Warranty', default=0.0, help="Warranty Rate")
    shipment_rate = fields.Float(string='Shipment', default=0.0, help="Shipment Rate")
    surcharge_rate = fields.Float('Surcharge', required=True, default=0.0, help="Surcharge Rate")
    pal_rate = fields.Float('PAL', required=True, default=0.0, help="Port Authority Levy Rate")
    eic_rate = fields.Float('EIC', required=True, default=0.0, help="Export Inspection Charge Rate")
    cess_levy_rate = fields.Float('Cess Levy', required=True, default=0.0, help="Cess Levy Rate")
    excise_duty_rate = fields.Float('Excise Duty', required=True, default=0.0, help="Excise Duty Rate")
    ridl_rate = fields.Float('RIDL', required=True, default=0.0, help="Road Infrastructure Development Levy Rate")
    srl_rate = fields.Float('SRL', required=True, default=0.0, help="Sugar Re-planting Levy Rate")
    sscl_rate = fields.Float('SSCL', required=True, default=0.0, help="Special Sales Tax on Cigarettes and Liquor Rate")
    vat_rate = fields.Float('VAT', required=True, default=0.15, help="Value Added Tax Rate")
    is_com_visible = fields.Boolean('COM Visible', compute='_compute_com_visible', store=False)
    is_exm_visible = fields.Boolean('EXM Visible', compute='_compute_exm_visible', store=False)
    is_cid_visible = fields.Boolean('CID Visible', compute='_compute_cid_visible', store=False)
    is_surcharge_visible = fields.Boolean('Surcharge Visible', compute='_compute_surcharge_visible', store=False)
    is_pal_visible = fields.Boolean('PAL Visible', compute='_compute_pal_visible', store=False)
    is_eic_visible = fields.Boolean('EIC Visible', compute='_compute_eic_visible', store=False)
    is_cess_levy_visible = fields.Boolean('Cess Levy Visible', compute='_compute_cess_levy_visible', store=False)
    is_excise_duty_visible = fields.Boolean('Excise Duty Visible', compute='_compute_excise_duty_visible', store=False)
    is_ridl_visible = fields.Boolean('RIDL Visible', compute='_compute_ridl_visible', store=False)
    is_srl_visible = fields.Boolean('SRL Visible', compute='_compute_srl_visible', store=False)
    is_sscl_visible = fields.Boolean('SSCL Visible', compute='_compute_sscl_visible', store=False)
    is_vat_visible = fields.Boolean('VAT Visible', compute='_compute_vat_visible', store=False)
    
    
    product_category_ids = fields.One2many(
        comodel_name="product.category",
        inverse_name="cw_harmonized_code_id",
        string="Product Categories",
        readonly=True,
    )
    product_template_ids = fields.One2many(
        comodel_name="product.template",
        inverse_name="cw_harmonized_code_id",
        string="Products",
        readonly=True,
    )
    product_category_count = fields.Integer(compute="_compute_product_category_count")
    product_template_count = fields.Integer(compute="_compute_product_template_count")
    # unique constraint on name
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "HS Code must be unique !"),
    ]
    
    def _compute_com_visible(self):
        for code in self:
            code.is_com_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.com_visible', False)

    def _compute_exm_visible(self):
        for code in self:
            code.is_exm_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.exm_visible', False)

    def _compute_cid_visible(self):
        for code in self:
            code.is_cid_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.cid_visible', False)

    def _compute_surcharge_visible(self):
        for code in self:
            code.is_surcharge_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.surcharge_visible', False)

    def _compute_pal_visible(self):
        for code in self:
            code.is_pal_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.pal_visible', False)

    def _compute_eic_visible(self):
        for code in self:
            code.is_eic_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.eic_visible', False)

    def _compute_cess_levy_visible(self):
        for code in self:
            code.is_cess_levy_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.cess_levy_visible', False)

    def _compute_excise_duty_visible(self):
        for code in self:
            code.is_excise_duty_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.excise_duty_visible', False)

    def _compute_ridl_visible(self):
        for code in self:
            code.is_ridl_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.ridl_visible', False)

    def _compute_srl_visible(self):
        for code in self:
            code.is_srl_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.srl_visible', False)

    def _compute_sscl_visible(self):
        for code in self:
            code.is_sscl_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.sscl_visible', False)

    def _compute_vat_visible(self):
        for code in self:
            code.is_vat_visible = self.env['ir.config_parameter'].sudo().get_param('cw_costing.vat_visible', False)

    @api.model
    def _default_company_id(self):
        return False

    @api.depends("product_category_ids")
    def _compute_product_category_count(self):
        for code in self:
            code.product_category_count = len(code.product_category_ids)

    @api.depends("product_template_ids")
    def _compute_product_template_count(self):
        for code in self:
            code.product_template_count = len(code.product_template_ids)
    
    