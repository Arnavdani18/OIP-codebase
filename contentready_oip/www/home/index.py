import frappe
from contentready_oip import api

def get_context(context):
    context.stats = api.get_homepage_stats()
    r = api.get_filters()
    context.update(r)
    context.problems = api.get_filtered_content('Problem', context.filter_location_lat, context.filter_location_lng, context.filter_location_range, context.filter_sectors, limit_page_length=5)
    context.solutions = api.get_filtered_content('Solution', context.filter_location_lat, context.filter_location_lng, context.filter_location_range, context.filter_sectors, limit_page_length=5)