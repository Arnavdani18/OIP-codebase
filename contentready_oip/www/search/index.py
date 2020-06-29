import frappe
from contentready_oip import api

def get_context(context):
    api.create_user_profile_if_missing(None,None,frappe.session.user)
    context.matched_problems = []
    context.matched_solutions = []
    context.matched_contributors = []
    context.available_sectors = api.get_available_sectors()
    context.key = ''
    parameters = frappe.form_dict
    try:
        key = parameters['key'].lower()
        location_name = parameters['loc_name'].split(", ") if "loc_name" in parameters else []
    except:
        key = ''
    if not key:
        return False
    context.key = key
    sectors = set()

    prepare_loc_filter = ''
    if location_name:
        prepare_loc_filter = "('city'={} OR 'state'={} AND 'country'={})".format(*location_name)
        
    # problems
    r = api.get_filtered_paginated_content(context, 'Problem', 'problems')
    context.update(r)
    context.matched_problems = api.get_searched_content('Problem', key, prepare_loc_filter)

    # solutions
    s = api.get_filtered_paginated_content(context, 'Solution', 'solutions')
    context.update(s)
    context.matched_solutions = api.get_searched_content('Solution', key, prepare_loc_filter)
    
    # User-Profile
    context.matched_contributors = api.get_content_recommended_for_user('User Profile', sectors)
    # print('\n\n\n', len(context.matched_problems), len(context.matched_solutions), '\n\n\n')