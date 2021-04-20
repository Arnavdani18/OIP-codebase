import frappe
import json

def get_context(context):
    params = frappe.form_dict
    if params.get('name'):
        doc = frappe.get_doc('Organisation', params['name'])
        try:
            # editing, check if user has write access
            doc.check_permission("write", "save")
        except:
            # if not, redirect them
            frappe.local.flags.redirect_location = '/organisations'
            raise frappe.Redirect
        context.doc = doc.as_json()
    context.available_service_categories = json.dumps(frappe.get_list('Service Category',fields=['title','name']))
    return context
