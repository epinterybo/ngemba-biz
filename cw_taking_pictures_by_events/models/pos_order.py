from odoo import models, api, fields
import logging
import base64
import requests

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    """
    picture_file_path = fields.Char(string="Picture File Path", readonly=True, default=False)
    picture_url = fields.Char(string="Picture URL", compute="_compute_picture_url")
    picture_data = fields.Binary(string="Picture", compute="_compute_picture_data", store=False)
    """
    
    cw_taken_picture_details_ids = fields.One2many('cw.taken.picture.details', 'pos_order_id', string='Camera pictures')
    
    """
    @api.depends('picture_file_path')
    def _compute_picture_url(self):
        for record in self:
            record.picture_url = record.picture_file_path if record.picture_file_path else False
            
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
    """
    
    def action_pos_order_paid(self):
        res = super().action_pos_order_paid()
        
        for order in self:
            pos_config_id = order.session_id.config_id.id
        
            camera_position = self.env['cw.taking.positions.cameras'].search([
                ('pos_config_id', '=', pos_config_id)
            ], limit=1)
            
            if camera_position:
                camera_position_lines = camera_position.cw_taking_positions_cameras_lines_ids
                """
                self.env['x_image_relations_line'].search([
                    ('x_studio_parent_record', '=', image_relation.id)
                ])
                """
                
                if camera_position_lines:
                    self.env['cw.event.manager.listener']
                    event_manager = self.env['cw.event.manager.listener']
                    
                    for camera_position_line in camera_position_lines:
                        if camera_position_line.camera_url and len(camera_position_line.camera_url) > 5:
                            _logger.info("Emitting event with info model_name: %s, model_id: %s", self._inherit, self.id)
                            event_manager.emit_event(event_name='image_should_be_taken', model_name=self._inherit, model_id=self.id, image_url=camera_position_line.camera_url)
                
        return res