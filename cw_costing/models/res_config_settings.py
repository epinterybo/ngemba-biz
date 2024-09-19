# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cw_com_visible = fields.Boolean(string="Cost of Manufacture, fixed amount per hs code (COM)", config_parameter='cw_costing.com_visible', default= False)
    cw_exm_visible = fields.Boolean(string="Export Market Value fixed amount per hs code (EXM)", config_parameter='cw_costing.exm_visible', default= False)
    cw_cid_visible = fields.Boolean(string="Customs Import Duty Rate (CID)", config_parameter='cw_costing.cid_visible', default= True)
    cw_surcharge_visible = fields.Boolean(string="Surcharge Rate", config_parameter='cw_costing.surcharge_visible', default= False)
    cw_pal_visible = fields.Boolean(string="Port Authority Levy Rate (PAL)", config_parameter='cw_costing.pal_visible', default= False)
    cw_eic_visible = fields.Boolean(string="Export Inspection Charge Rate (EIC)", config_parameter='cw_costing.eic_visible', default= False)
    cw_cess_levy_visible = fields.Boolean(string="Cess Levy Rate", config_parameter='cw_costing.cess_levy_visible', default=False)
    cw_excise_duty_visible = fields.Boolean(string="Excise Duty Rate", config_parameter='cw_costing.excise_duty_visible', default=False)
    cw_ridl_visible = fields.Boolean(string="Road Infrastructure Development Levy Rate (RIDL)", config_parameter='cw_costing.ridl_visible', default=False)
    cw_srl_visible = fields.Boolean(string="Sugar Re-planting Levy Rate (SRL)", config_parameter='cw_costing.srl_visible', default=False)
    cw_sscl_visible = fields.Boolean(string="Special Sales Tax on Cigarettes and Liquor Rate (SSCL)", config_parameter='cw_costing.sscl_visible', default=False)
    cw_vat_visible = fields.Boolean(string="Value Added Tax Rate (VAT)", config_parameter='cw_costing.vat_visible', default=True)
    cw_customs_bill_visible = fields.Boolean(string="Generate Customs Bill from the Landed Costs", config_parameter='cw_costing.customs_bill_visible', default=False)
    cw_shipping_bill_visible = fields.Boolean(string="Generate Shipping Bill from the Landed Costs", config_parameter='cw_costing.shipping_bill_visible', default=False)
