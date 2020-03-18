import frappe
from contentready_oip import api

def get_context(context):
    parameters = frappe.form_dict
    try:
        context.page = int(parameters['page'])
    except:
        context.page = 1
    context.total_count = api.get_homepage_stats()['problems']
    limit_start = context.page - 1
    limit_page_length = 20
    context.start = limit_start*limit_page_length
    context.end = context.start + limit_page_length
    context.limit_page_length = limit_page_length
    context.limit_start = limit_start
    if context.end > context.total_count:
        context.end = context.total_count
    r = api.get_filters()
    context.update(r)
    
    context.has_next_page = False
    if context.total_count > limit_page_length*context.page:
        context.has_next_page = True
    if frappe.session.user != 'Guest':
        context.problems = api.get_filtered_content('Problem', context.filter_location_lat, context.filter_location_lng, context.filter_location_range, context.filter_sectors, limit_page_length=limit_page_length, limit_start=limit_start)