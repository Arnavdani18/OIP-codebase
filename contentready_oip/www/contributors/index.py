import frappe
from contentready_oip import api

def get_context(context):
    doctype = 'User Profile'
    r = api.get_filtered_paginated_content(context, doctype, 'users')
    context.update(r)