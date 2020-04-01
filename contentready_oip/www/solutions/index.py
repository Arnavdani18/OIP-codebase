import frappe
from contentready_oip import api
import json

def get_context(context):
    api.create_user_profile_if_missing(None,None,frappe.session.user)
    doctype = 'Solution'
    r = api.get_filtered_paginated_content(context, doctype, 'solutions')
    context.update(r)