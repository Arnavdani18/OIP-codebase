import frappe
from contentready_oip import api

def get_context(context):
    api.create_user_profile_if_missing(None,None,frappe.session.user)
    doctype = 'User Profile'
    r = api.get_filtered_paginated_content(context, doctype, 'users')
    context.update(r)
    # context.users =  api.search_contributors_by_text('', limit_page_length=20,html=False)