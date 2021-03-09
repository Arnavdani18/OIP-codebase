"""
Backend for search route
"""
import json
from geopy.distance import distance
import frappe
from contentready_oip import api, problem_search, solution_search, user_search

modules = {
    'Problem': problem_search,
    'Solution': solution_search,
    'User Profile': user_search,
}

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
    context.key = ''
    context.available_sectors = api.get_available_sectors()
    parameters = frappe.form_dict
    scope = {}
    try:
        context.key = parameters['key'].lower()
        scope['sectors'] = json.loads(parameters['sectors']) if "sectors" in parameters else []
        scope['sdg'] = json.loads(parameters['sdg']) if parameters.get("sdg") else []
        # scope['beneficiaries'] = json.loads(parameters['beneficiaries']) if parameters.get("beneficiaries") else []
    except Exception as e:
        print(str(e))
    if not context.key:
        return False
    
    context.matched_problems = search_doctype('Problem', context.key, scope)
    context.matched_solutions = search_doctype('Solution', context.key, scope)
    # For contributors, we filter by sectors across the matched problems and solutions
    sectors = set()
    for doc in context.matched_problems + context.matched_solutions:
        for s in doc.sectors:
            sectors.add(s.sector)
    scope['sectors'] = sectors
    # An empty sector list will match every user so we pre-empt this search
    if len(scope['sectors']):
        context.matched_contributors = search_doctype('User Profile', '*', scope)
    return context
    

def search_doctype(doctype, key, scope=None):
    matched = modules[doctype].search_index(key, scope=scope)
    return [frappe.get_doc(doctype, d['name']) for d in matched]
    