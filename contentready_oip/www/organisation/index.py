import frappe
import json

def get_context(context):
    context.available_service_categories = json.dumps(frappe.get_list('Service Category',fields=['title','name']))
    return context
