import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def mta_request(
        method=None, 
        url=None, 
        headers={'Content-Type': 'application/json'}, 
        data=None, 
        params=None):
    
    try:
        response = requests.request(method=method, url=url, headers=headers, data=data, params=params)
        response_code, response_dict = response.status_code, json.loads(response.text)

    except Exception as e:
        logger.info(f"Error occurred while making a request to {url}: {str(e)}", exc_info=True) 
        return None
    
    return response_dict