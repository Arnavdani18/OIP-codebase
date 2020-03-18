import frappe
from contentready_oip import api
import json
def get_context(context):
    # set default filters
    # these will be overridden by query parameters if provided
    if frappe.session.user == 'Guest':
        r = {
            'filter_location_name': None,
            'filter_location_lat': None,
            'filter_location_lng': None,
            'filter_location_range': None,
            'filter_sectors': None,
        }
    else:
        r = api.get_filters()
        context.update(r)
    context.available_sectors = api.get_available_sectors()
    parameters = frappe.form_dict
    # page
    try:
        context.page = int(parameters['page'])
    except:
        context.page = 1
    # filter_location_name
    try:
        context.filter_location_name = parameters['loc']
    except:
        pass
    # filter_location_lat
    try:
        context.filter_location_lat = float(parameters['lat'])
    except:
        pass
    # filter_location_lng
    try:
        context.filter_location_lng = float(parameters['lng'])
    except:
        pass
    # filter_location_range
    try:
        context.filter_location_range = int(parameters['rng'])
    except:
        pass
    # filter_sectors
    try:
        context.filter_sectors = json.loads(parameters['sectors'])
    except Exception as e:
        print(str(e))
        pass
    limit_start = context.page - 1
    limit_page_length = 20
    context.solutions = api.get_filtered_content('Solution', context.filter_location_lat, context.filter_location_lng, context.filter_location_range, context.filter_sectors, limit_page_length=limit_page_length, limit_start=limit_start)
    context.start = limit_start*limit_page_length
    context.end = context.start + limit_page_length
    context.total_count = len(context.solutions)
    if context.end > context.total_count:
        context.end = context.total_count
    context.has_next_page = False
    if context.total_count > limit_page_length*context.page:
        context.has_next_page = True