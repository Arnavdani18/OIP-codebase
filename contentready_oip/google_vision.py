import os
import frappe
from frappe.utils import get_site_path
from google.cloud import vision

@frappe.whitelist(allow_guest=False)
def is_content_explicit(file_url):
    try:
        # We need to strip the leading '/' from file_url to get actual absolute path
        file_url = file_url[1:]
        # Prepend public if it's not a private file
        if not file_url.startswith('private'):
            file_url = 'public/' + file_url
        file_path = os.path.join(get_site_path(), file_url)
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # set up vision_client
        vision_api_service_key = frappe.get_value('OIP Configuration', '', 'vision_api_service_key')[1:]
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(os.path.join(get_site_path(), vision_api_service_key))
        client = vision.ImageAnnotatorClient()

        # get thresholds from config
        adult_threshold = int(frappe.get_value('OIP Configuration', '', 'adult'))
        medical_threshold = int(frappe.get_value('OIP Configuration', '', 'medical'))
        spoof_threshold = int(frappe.get_value('OIP Configuration', '', 'spoof'))
        violence_threshold = int(frappe.get_value('OIP Configuration', '', 'violence'))
        racy_threshold = int(frappe.get_value('OIP Configuration', '', 'racy'))

        # perform label detection
        image = vision.types.Image(content=content)
        response = client.safe_search_detection(image=image)
        annotations = response.safe_search_annotation

        print(annotations)

        # check if score over thresholds
        if annotations.adult > adult_threshold or \
            annotations.medical > medical_threshold or \
            annotations.spoof > spoof_threshold or \
            annotations.violence > violence_threshold or \
            annotations.racy > racy_threshold:
            return True

        return False
        
    except Exception as e:
        print("detect_explicit_content:\n\n",str(e))
        raise