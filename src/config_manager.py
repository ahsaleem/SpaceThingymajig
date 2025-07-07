import os
import json
import logging
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / '.satellite_simulator'
        self.config_file = self.config_dir / 'config.json'
        self.config = {}
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        try:
            self.config_dir.mkdir(exist_ok=True)
            if not self.config_file.exists():
                self.config_file.touch()
                self.save_config()
        except Exception as e:
            logging.error(f"Error creating config directory: {str(e)}")
    
    def load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {str(e)}")
            self.config = {}
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving config: {str(e)}")
    
    def get_api_key(self):
        return self.config.get('n2yo_api_key', '')
    
    def set_api_key(self, api_key):
        self.config['n2yo_api_key'] = api_key
        self.save_config()
        # Update environment variable
        os.environ['N2YO_API_KEY'] = api_key 