from odoo import models, fields, api

class RewardCardWizard(models.TransientModel):
    _name = 'cw.reward.card.wizard'
    _description = 'CW Reward Card Wizard'

    import_file = fields.Binary(string='Import File')
    initial_points = fields.Float(string='Initial Points', default=0)
    generate_cards_count = fields.Integer(string='Number of Cards to Generate', default=0)

    def import_cards(self):
        # Implement logic to import reward cards from the file
        if self.import_file:
            # Example: process the file and create reward cards
            import base64
            import csv
            file_content = base64.b64decode(self.import_file)
            file_content = file_content.decode('utf-8')
            csv_data = csv.reader(file_content.split('\n'), delimiter=',')
            for row in csv_data:
                if row:
                    card_number, points = row
                    self.env['cw.reward.card'].create({'name': card_number, 'total_points': float(points)})

    def generate_cards(self):
        for _ in range(self.generate_cards_count):
            self.env['cw.reward.card'].create({
                'name': self.env['ir.sequence'].next_by_code('cw.reward.card'),
                'total_points': self.initial_points
            })
