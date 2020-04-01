import frappe
from contentready_oip import api
import json

def get_context(context):
    api.create_user_profile_if_missing(None,None,frappe.session.user)
    doctype = 'Problem'
    r = api.get_filtered_paginated_content(context, doctype, 'problems')
    context.update(r)
    