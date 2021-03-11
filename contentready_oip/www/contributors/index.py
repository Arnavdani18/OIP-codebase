import frappe
from contentready_oip import api

def get_context(context):
    doctype = 'User Profile'
    r = api.get_filtered_paginated_content(context, doctype, 'users')
    skip = ['Guest', 'Administrator', 'admin@example.com']
    for index, u in enumerate(r['users']):
        if u.name in skip or not(u.first_name or u.last_name):
            del r['users'][index]
    context.update(r)
    # context.users =  api.search_contributors_by_text('', limit_page_length=20,html=False)