from odoo import models, fields, api
import logging
import base64

_logger = logging.getLogger(__name__)

class CwTakenPictureDetails(models.Model):
    _name = 'cw.taken.picture.details'
    _description = 'CW Taken Picture Details'
    
    picture_file_path = fields.Char(string="Picture File Path", readonly=True, default=False)
    #picture_url = fields.Char(string="Picture URL", compute="_compute_picture_url")
    picture_data = fields.Binary(string="Picture", compute="_compute_picture_data", store=False)
    pos_order_id = fields.Many2one('pos.order', string="Pos Order")
    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking')
    is_file_verified = fields.Boolean('is file verified', default=False)
    
    """
    @api.depends('picture_file_path')
    def _compute_picture_url(self):
        for record in self:
            record.picture_url = record.picture_file_path if record.picture_file_path else False
    """
            
    @api.depends('picture_file_path')
    def _compute_picture_data(self):
        for record in self:
            if record.picture_file_path:
                _logger.info("Image full Path is %s 001", record.picture_file_path)
                try:
                    _logger.info("Image full Path is %s 002", record.picture_file_path)
                    with open(record.picture_file_path, "rb") as image_file:
                        _logger.info("Image full Path is %s 003", record.picture_file_path)
                        record.picture_data = base64.b64encode(image_file.read())
                except Exception:
                    _logger.info("Image full Path is %s 004", record.picture_file_path)
                    record.picture_data = False
            else:
                _logger.info("Image full Path is %s 005", record.picture_file_path)
                record.picture_data = False
    
    @api.model
    def clean_non_existing_files(self):
        last_records = self.search([('is_file_verified', '=', False)], limit=100, order='create_date ASC')
        
        for record in last_records:
            try:
                _logger.info("file %s exist", record.picture_file_path)
                with open(record.picture_file_path, "rb") as image_file:
                    record.write({
                        'is_file_verified': True
                    })
            except Exception:
                record.unlink()