import requests
from odoo import models, api
from odoo.api import Environment, SUPERUSER_ID
from requests.auth import HTTPDigestAuth
import os
from datetime import datetime
import concurrent.futures


import logging
_logger = logging.getLogger(__name__)

class CWEventListener(models.Model):
    _name = 'cw.event.manager.listener'
    
    _url = 'http://192.168.3.179/ISAPI/Streaming/channels/1/picture'
    #_url = 'http://m.cw.vu:8051/ISAPI/Streaming/channels/1/picture'
    _auth_username = 'odoo'
    _auth_password = 'Snaitkla093'
    
    _events = {}
    
    @api.model
    def register_event(self, event_name, callback):
        """ Register a new event listener for a specific event """
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append(callback)
        
    @api.model
    def emit_event(self, event_name, **kwargs):
        """ Emit an event, triggering all listeners registered for this event """
        if event_name in self._events:
            for callback in self._events[event_name]:
                callback(**kwargs)
    
    def get_output_directory(self):
        # Get the root directory of the current module
        module_root_dir = os.path.dirname(os.path.abspath(__file__))
        module_root_dir = os.path.abspath(os.path.join(module_root_dir, os.pardir))
        # Define the output directory path
        output_dir = os.path.join(module_root_dir, 'snapshots_pics')

        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        return output_dir
    
    def get_output_directory_log(self):
        # Get the root directory of the current module
        module_root_dir = os.path.dirname(os.path.abspath(__file__))
        module_root_dir = os.path.abspath(os.path.join(module_root_dir, os.pardir))
        # Define the output directory path
        output_dir = os.path.join(module_root_dir, 'snapshots_pics_logs')

        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        return output_dir
    
    
    def create_timestamped_file(self):
        # Create a filename with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_{timestamp}.jpg"
        return filename
    
    
    def write_data_to_file(self, filepath, data):
        # Open the file in append mode and write data with a newline character
        try:
            with open(filepath, 'a') as file:
                file.write(data + '\n')
        except Exception as e:
            _logger.info("Error writing to file %s, and error is %s", filepath, e)
            print(f"Error writing to file {filepath}: {str(e)}")
    
    
    @api.model
    def set_image_capture_listener(self, **kwargs):
        model_name = kwargs.get('model_name')
        model_id = kwargs.get('model_id')
        field_name = kwargs.get('field_name')
        
        model_obj = self.env[model_name]
        model_record = model_obj.browse(model_id)
        
        if not model_record:
            _logger.info("CWEventListener - set_image_capture_listener:  Now record found for model %s, with id %s", model_name, model_id)
            return
        
        if not hasattr(model_obj, field_name):
            _logger.info("CWEventListener - set_image_capture_listener:  Now field found for model %s, with field name %s", model_name, field_name)
            return
        
        # Generate the file name with timestamp
        filename = self.create_timestamped_file()
        filename_log = filename + ".txt"
        output_dir = self.get_output_directory()
        file_path = os.path.join(output_dir, filename)
        file_path_log = os.path.join(output_dir, filename_log)
        
        self.write_data_to_file(filepath=file_path_log, data=f"About create file {filename} related to the model {model_name} with record id {model_id}")
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.saving_image_async, model_record=model_record, field_name=field_name, file_path=file_path, file_path_log=file_path_log)
            future.add_done_callback(self.saving_image_async_call_back(model_record=model_record, field_name=field_name, file_path=file_path, file_path_log=file_path_log))
        
        
            
    def saving_image_async(self, model_record, field_name, file_path, file_path_log):
        # Send a GET request to the URL with digest authentication
        try:
            response = requests.get(self._url, auth=HTTPDigestAuth(self._auth_username, self._auth_password))
            
            # Check if the request was successful
            if response.status_code == 200:
                # Save the image to a file
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                _logger.info('Image downloaded and saved as %s', file_path)
                self.write_data_to_file(filepath=file_path_log, data=f"Image downloaded and saved as {file_path}")
            else:
                _logger.info('Failed to download image. Status code: %s', response.status_code)
                self.write_data_to_file(filepath=file_path_log, data=f"Failed to download image. Status code: {response.status_code}")
                _logger.info('Response: %s', response.text)
                self.write_data_to_file(filepath=file_path_log, data="Response : " + response.text)
                #print(f'Failed to download image. Status code: {response.status_code}')
                #print('Response:', response.text)
                model_record.write({
                    field_name: file_path,
                })
        except requests.exceptions.RequestException as e:
            _logger.info('An error occurred: %s', e)
            self.write_data_to_file(filepath=file_path_log, data=f'An error occurred: {e}')
            #print(f'An error occurred: {e}')
            
    def saving_image_async_call_back(self, **kwargs):
        model_record = kwargs.get('model_record')
        field_name = kwargs.get('field_name')
        file_path = kwargs.get('file_path')
        file_path_log = kwargs.get('file_path_log')
        
        def callback(future):
            try:
                result = future.result()
                self.write_data_to_file(filepath=file_path_log, data='Result : ' + result)
            except Exception as e:
                self.write_data_to_file(filepath=file_path_log, data=f"Handling Async called result failed: {e}")
                
def register_event_listener(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    event_manager = env['cw.event.manager.listener']
    event_manager.register_event('image_should_be_taken', event_manager.set_image_capture_listener)