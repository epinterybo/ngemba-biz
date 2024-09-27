import re
from datetime import datetime
from odoo import api, models
from odoo.exceptions import UserError


class BankReport(models.AbstractModel):
    _name = 'report.ybo_pos_cash_move.report_pos_cash_move'
    _description = 'Report  POS Cash Move'

    def _get_report_values(self, docids, data=None):
        docs = self.env['ybo_pos_cash_move.pos_cash_report'].browse(docids)
        
        
        if docs.state != "approved" :
            raise UserError("You can only generate a Bank Report for approved operation")


        # List of bill fields
        bill_fields = [
            'total_5_vt', 'total_10_vt', 'total_20_vt', 'total_50_vt',
            'total_100_vt', 'total_200_vt', 'total_500_vt', 'total_1000_vt',
            'total_2000_vt', 'total_5000_vt', 'total_10000_vt'
        ]

        # Initialize totals
        bills = {field: 0 for field in bill_fields}

        # Calculate sums
        for doc in docs:
            for field in bill_fields:
                bills[field] += int(getattr(doc, field, 0))

        # Calculate total coins
        total_coins = sum(
            bills.get(key, 0) for key in ['total_100_vt', 'total_50_vt', 'total_20_vt', 'total_10_vt', 'total_5_vt'])
        
        
        # get check
        
        cheques = doc.cheques_id
        
        total_cheq_anz = 0
        total_cheq_other = 0
        
        for elt in cheques :
            if elt.bank.lower() == "anz" or elt.bank.lower() == "anz2" :
                total_cheq_anz = total_cheq_anz + elt.amount
            else :
                total_cheq_other = total_cheq_other + elt.amount
    
        

        # Calculate total notes
        total_notes = sum(bills.get(key, 0) for key in
                         ['total_200_vt', 'total_500_vt', 'total_1000_vt', 'total_2000_vt', 'total_5000_vt',
                          'total_10000_vt'])
        return {
            'bills': bills,
            'totalcoins': total_coins,
            'totalnotes': total_notes,
            "cheques" : cheques,
            "total_cheq_other" : total_cheq_other,
            "total_cheq_anz" : total_cheq_anz,
            'date': datetime.now().strftime("%d/%m/%Y"),
        }
