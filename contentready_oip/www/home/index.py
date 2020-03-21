import frappe
from contentready_oip import api

def get_context(context):
    context.full_width = True
    context.stats = api.get_homepage_stats()
    p = api.get_filtered_paginated_content(context, 'Problem', 'problems', limit_page_length=5)
    context.update(p)
    s = api.get_filtered_paginated_content(context, 'Solution', 'solutions', limit_page_length=5)
    context.update(s)