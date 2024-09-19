from odoo import models, fields, _, api

class PosCashCheque(models.Model):
    _name = 'ybo_pos_cash_move.pos_cash_cheque'
    _description = 'POS Cash Cheque'
    #_rec_name = "reference_code"
    #_sql_constraints = [
    #    ('reference_code_uniq', 'unique(reference_code)', 'Reference number must be unique!')
    #]

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(string='Amount', required=True, 
                                    currency_field='currency_id',readonly=True)
    account_number = fields.Text(string='Account #' , default="")
    drawer = fields.Text(string='Drawer', default="")
    bank = fields.Text(string='Bank', default="")
    cheque_number = fields.Text(string='Cheque #', default="")
    
    pos_cash_report_id = fields.Many2one('ybo_pos_cash_move.pos_cash_report', string='POS Cash Report', required=True, readonly=True,ondelete='cascade')
