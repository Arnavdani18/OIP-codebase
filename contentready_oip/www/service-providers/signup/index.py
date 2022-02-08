import frappe
import json
from contentready_oip import api

def get_context(context):
    frappe.local.flags.redirect_location = '/'
    raise frappe.Redirect
    context.available_categories = api.get_service_categories()
    context.organisation = {
        "title": "",
        "service_category": "",
        "website": "",
        "email": "",
        "phone": "",
        "city": "",
        "state": "",
        "country": "",
        "name": ""
    }
    # get user's org and fill context
    if frappe.session.user != "Guest":
        orgs = frappe.get_list("Organisation", fields=["name", "title", "service_category", "website", "email", "phone", "city", "state", "country"], filters={"email": frappe.session.user, "type": "Service Provider"}, limit=1)
        if len(orgs) > 0:
            context.organisation = orgs[0]