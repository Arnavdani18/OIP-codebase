import frappe
from contentready_oip import api

def get_context(context):
    context.full_width = True
    context.stats = api.get_homepage_stats()
    context = api.get_content_for_context(context, 'Problem', 'problems', limit_page_length=5)
    context = api.get_content_for_context(context, 'Solution', 'solutions', limit_page_length=5)
