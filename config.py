#!/usr/bin/env python3
"""
Configuration Module
Handles saving and loading application settings.
"""

import os
import json
from typing import Dict, Any, Optional

# Default configuration file location
CONFIG_DIR = os.path.expanduser("~/.batch_image_ocr")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Default configuration
DEFAULT_CONFIG = {
    "tesseract_path": None,
    "last_output_dir": None,
    "last_input_dir": None
}


def ensure_config_dir() -> None:
    """Ensure the configuration directory exists"""
    if not os.path.exists(CONFIG_DIR):
        try:
            os.makedirs(CONFIG_DIR)
        except Exception as e:
            print(f"Warning: Could not create config directory: {e}")


def load_config() -> Dict[str, Any]:
    """
    Load configuration from file
    
    Returns:
        Dictionary containing configuration values
    """
    ensure_config_dir()
    
    # If config file doesn't exist, return defaults
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            
        # Ensure all expected keys are present
        for key in DEFAULT_CONFIG:
            if key not in config:
                config[key] = DEFAULT_CONFIG[key]
                
        return config
    except Exception as e:
        print(f"Warning: Could not load config file: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to file
    
    Args:
        config: Dictionary containing configuration values
        
    Returns:
        True if successful, False otherwise
    """
    ensure_config_dir()
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Warning: Could not save config file: {e}")
        return False


def update_config(key: str, value: Any) -> bool:
    """
    Update a single configuration value
    
    Args:
        key: Configuration key to update
        value: New value
        
    Returns:
        True if successful, False otherwise
    """
    config = load_config()
    config[key] = value
    return save_config(config)


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a configuration value
    
    Args:
        key: Configuration key to retrieve
        default: Default value if key is not found
        
    Returns:
        Configuration value or default
    """
    config = load_config()
    return config.get(key, default)
