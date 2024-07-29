import logging.config
import yaml
from pathlib import Path

def setup_logging(default_path='app/config/log_config.yml', default_level=logging.INFO):
    """
    Setup logging configuration from a YAML file.
    """
    if Path(default_path).exists():
        with open(default_path, 'r') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        print(f"Warning: Could not find logging configuration file at {default_path}. Using default logging configuration.")

# Call this function to initialize logging
