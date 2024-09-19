import requests
from odoo import models, api
from odoo.api import Environment, SUPERUSER_ID
from requests.auth import HTTPDigestAuth
import os
from datetime import datetime
import concurrent.futures
import threading
import random
import logging
from odoo.addons.bus.models.bus import dispatch
import csv

_logger = logging.getLogger(__name__)

class CWEventListener(models.Model):
    _name = 'cw.event.manager.listener'
    
    _url = 'http://192.168.3.179/ISAPI/Streaming/channels/1/picture'
    _auth_username = 'odoo'
    _auth_password = 'Snaitkla093'
    
    _events = {}
    
    @api.model
    def register_event(self, event_name, callback):
        """ Register a new event listener for a specific event """
        _logger.info("register_event  called with %s and callback function %s", event_name, callback)
        if event_name not in self._events:
            _logger.info("if Event Name for event %s", event_name)
            self._events[event_name] = []
        self._events[event_name].append(callback)
        _logger.info("self._events is %s", self._events)
        
    @api.model
    def emit_event(self, event_name, model_name, model_id, image_url):
        """ Emit an event, triggering all listeners registered for this event """
        _logger.info("Reception of emit committed %s, %s, %s", event_name, model_name, model_id)
        _logger.info("Self Event is %s", self._events)
        self.set_image_capture_listener(model_name=model_name, model_id=model_id, image_url=image_url)
        if event_name in self._events:
            _logger.info("we have this event here : %s", event_name)
            for callback in self._events[event_name]:
                _logger.info("calling back function from emit_event: %s", callback)
                callback(model_name, model_id)
    
    def get_output_directory(self):
        module_root_dir = os.path.dirname(os.path.abspath(__file__))
        module_root_dir = os.path.abspath(os.path.join(module_root_dir, os.pardir))
        output_dir = os.path.join(module_root_dir, 'snapshots_pics')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir
    
    def get_output_directory_csv(self):
        module_root_dir = os.path.dirname(os.path.abspath(__file__))
        module_root_dir = os.path.abspath(os.path.join(module_root_dir, os.pardir))
        output_dir = os.path.join(module_root_dir, 'snapshots_csv')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir
    
    def get_output_directory_log(self):
        module_root_dir = os.path.dirname(os.path.abspath(__file__))
        module_root_dir = os.path.abspath(os.path.join(module_root_dir, os.pardir))
        output_dir = os.path.join(module_root_dir, 'snapshots_pics_logs')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir
    
    def create_timestamped_file(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_number = random.randint(1000, 9999)
        filename = f"data_{timestamp}_{random_number}.jpg"
        return filename
    
    def write_data_to_file(self, filepath, data):
        try:
            with open(filepath, 'a') as file:
                file.write(data + '\n')
        except Exception as e:
            _logger.info("Error writing to file %s, and error is %s", filepath, e)
    
    @api.model
    def set_image_capture_listener(self, model_name, model_id, image_url):
        """
        _logger.info("Emit event set_image_capture_listener: %s", **kwargs)
        model_name = kwargs.get('model_name')
        model_id = kwargs.get('model_id')
        field_name = kwargs.get('field_name')
        """
        # Ensure model_name is a string
        if isinstance(model_name, list):
            model_name = model_name[0]
        
        _logger.info("Emit calling information model_name: %s, model_id: %s, ", model_name, model_id)
        
        _logger.info("Do I have issue at this level 000: %s, model_id: %s, ", model_name, model_id)
        
        model_obj = self.env[model_name]
        _logger.info("Do I have issue at this level 001: %s, model_id: %s, ", model_name, model_id)
        model_record = model_obj.browse(model_id)
        
        _logger.info("After record 001 Emit calling information model_name: %s, model_id: %s, ", model_name, model_id)
        
        if not model_record:
            _logger.info("CWEventListener - set_image_capture_listener: No record found for model %s, with id %s", model_name, model_id)
            return
        
        """
        if not hasattr(model_obj, field_name):
            _logger.info("CWEventListener - set_image_capture_listener: No field found for model %s, with field name %s", model_name, field_name)
            return
        """
        
        _logger.info("After record 002 Emit calling information model_name: %s, model_id: %s, ", model_name, model_id)
        
        filename = self.create_timestamped_file()
        filename_log = filename + ".txt"
        filename_csv = filename + ".csv"
        output_dir = self.get_output_directory()
        file_path = os.path.join(output_dir, filename)
        file_path_log = os.path.join(self.get_output_directory_log(), filename_log)
        file_path_csv = os.path.join(self.get_output_directory_csv(), filename_csv)
        
        _logger.info("After record 003 Emit calling information model_name: %s, model_id: %s, ", model_name, model_id)
        
        self.write_data_to_file(filepath=file_path_log, data=f"About to create file {filename} related to the model {model_name} with record id {model_id}")
        
        _logger.info("After record 004 Emit calling information model_name: %s, model_id: %s", model_name, model_id)
        
        #saving the pictures before launching the capture in seprated thread
        record_values = {}
        record_values['picture_file_path'] = file_path
        if model_name == 'pos.order':
            record_values['pos_order_id'] = model_record.id
        elif model_name == 'stock.picking':
            record_values['stock_picking_id'] = model_record.id
        
        record_save = self.env['cw.taken.picture.details'].create(record_values)
        
        
        # Create a separate thread for image capture
        thread = threading.Thread(target=self.saving_image_async, args=(model_record, file_path, file_path_log, image_url, model_name, file_path_csv))
        thread.start()
        
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.saving_image_async, model_record=model_record, file_path=file_path, file_path_log=file_path_log, image_url=image_url, model_name=model_name)
            #future.add_done_callback(self.saving_image_async_call_back(model_record=model_record, file_path=file_path, file_path_log=file_path_log))
        """
        _logger.info("After record 005 Emit calling information model_name: %s, model_id: %s", model_name, model_id)
            
    def saving_image_async(self, model_record, file_path, file_path_log, image_url, model_name, file_path_csv):
        _logger.info("After entering saving_image_async")
        try:
            response = requests.get(image_url, auth=HTTPDigestAuth(self._auth_username, self._auth_password))
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                _logger.info('Image downloaded and saved as %s', file_path)
                self.write_data_to_file(filepath=file_path_log, data=f"Image downloaded and saved as {file_path}")
                
                with open(file_path_csv, mode='w', newline='', encoding='utf-8') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    # Write the header
                    header = ['model_name', 'model_record_id', 'file_path']
                    csv_writer.writerow(header)
                    csv_writer.writerow([model_name, model_record.id, file_path])
                        
                        
                #model_record.write({field_name: file_path})
                
                # Notify the main thread to save the record using the bus
                """
                channel_id = f'channel-image-{model_name}-{model_record.id}'
                self.env['bus.bus']._sendone(
                    channel_id,
                    'save_image_record',
                    {
                        'model_record_id': model_record.id,
                        'file_path': file_path,
                        'model_name': model_name
                    }
                )
                """
                
                """
                record_values = {}
                record_values['picture_file_path'] = file_path
                if model_name == 'pos.order':
                    record_values['pos_order_id'] = model_record.id
                elif model_name == 'stock.picking':
                    record_values['stock_picking_id'] = model_record.id
                
                record_save = self.env['cw.taken.picture.details'].create(record_values)
                _logger.info('Image %s saved in Database as %s', file_path, record_save)
                """
                
                
            else:
                _logger.info('Failed to download image. Status code: %s', response.status_code)
                self.write_data_to_file(filepath=file_path_log, data=f"Failed to download image. Status code: {response.status_code}")
                _logger.info('Response: %s', response.text)
                self.write_data_to_file(filepath=file_path_log, data="Response: " + response.text)
            
            
        except requests.exceptions.RequestException as e:
            _logger.info('An error occurred: %s', e)
            self.write_data_to_file(filepath=file_path_log, data=f'An error occurred: {e}')
        
            
        @api.model
        def handle_save_image_record(self, message):
            """Save the image record in the main thread to avoid threading issues with Odoo's ORM"""
            _logger.info("Handling save_image_record with message: %s", message)
            model_record_id = message['model_record_id']
            file_path = message['file_path']
            model_name = message['model_name']
            
            record_values = {'picture_file_path': file_path}
            #model_obj = self.env[model_name].browse(model_record_id)
            if model_name == 'pos.order':
                record_values['pos_order_id'] = model_record_id
            elif model_name == 'stock.picking':
                record_values['stock_picking_id'] = model_record_id
                    
            self.env['cw.taken.picture.details'].create(record_values)
            
            
    def saving_image_async_call_back(self, model_record, file_path, file_path_log):
        """
        model_record = kwargs.get('model_record')
        file_path = kwargs.get('file_path')
        file_path_log = kwargs.get('file_path_log')
        """
        
        def callback(future):
            try:
                result = future.result()
                self.write_data_to_file(filepath=file_path_log, data='Result: ' + result)
            except Exception as e:
                self.write_data_to_file(filepath=file_path_log, data=f"Handling async callback result failed: {e}")
                
        return callback
    
    

#def register_event_listener(cr, registry):
#env = api.Environment(cr, SUPERUSER_ID, {})
def register_event_listener(env):
    _logger.info("register_event_listener called at this level")
    event_manager = env['cw.event.manager.listener']
    event_manager.register_event('image_should_be_taken', event_manager.set_image_capture_listener)
    # Subscribe to the bus channel
    #env['bus.bus']._sendone('cw_event_manager', 'dummy', {})  # Dummy send to ensure the channel is created
    #env['bus.bus']._poll([('cw_event_manager', 'save_image_record')])
    
    
    """"
    @api.model
    def dispatch_message(self, message):
        if message['type'] == 'save_image_record':
            self.env['cw.event.manager.listener'].handle_save_image_record(message['payload'])

    env['bus.bus']._poll([('cw_event_manager',)], dispatch_message)
    """
