import frappe
from contentready_oip import api

def get_context(context):
    r = api.get_filters()
    context.update(r)
    if frappe.session.user != 'Guest':
        context.solutions = api.get_filtered_content('Solution', context.filter_location_lat, context.filter_location_lng, context.filter_location_range, context.filter_sectors)
