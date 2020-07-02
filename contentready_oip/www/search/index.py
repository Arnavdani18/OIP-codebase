"""
Backend for search route
"""
import json
from geopy.distance import distance
import frappe
from contentready_oip import api

def get_lat_lng_by_rng(lat, lng, rng):
    """
    Return latitude and longitude after applying distance(KM) to it
    """
    lat, lng, rng = float(lat), float(lng), int(rng)
    _d = distance.distance(kilometers=rng).destination((lat, lng), 90)
    return(_d.latitude, _d.longitude)

def get_context(context):
    """
    This will execute while page load. default to get context of the page.
    """
    api.create_user_profile_if_missing(None, None, frappe.session.user)
    context.matched_problems = []
    context.matched_solutions = []
    context.matched_contributors = []
    context.available_sectors = api.get_available_sectors()
    context.key = ''
    parameters = frappe.form_dict
    try:
        key = parameters['key'].lower()
        sector_list = json.loads(parameters['sectors']) if "sectors" in parameters else []
    except:
        key = ''
    if not key:
        return False
    context.key = key
    sectors = set()

    prepare_sector_filter = ''
    filter_str = " AND meili_sectors=".join(sector_list) if not "all" in sector_list else ''
    if filter_str:
        prepare_sector_filter = "meili_sectors=" + filter_str

    # problems
    _r = api.get_filtered_paginated_content(context, 'Problem', 'problems')
    context.update(_r)
    context.matched_problems = api.get_searched_content('Problem', key, prepare_sector_filter)

    # solutions
    _s = api.get_filtered_paginated_content(context, 'Solution', 'solutions')
    context.update(_s)
    context.matched_solutions = api.get_searched_content('Solution', key, prepare_sector_filter)

    # User-Profile
    context.matched_contributors = api.get_content_recommended_for_user('User Profile', sectors)
    # print('\n\n\n', len(context.matched_problems), len(context.matched_solutions), '\n\n\n')
