import frappe
import json
from contentready_oip import api, organisation_search

RESULTS_PER_PAGE = 20

def get_context(context):
    context.available_sectors = api.get_available_sectors()
    context.available_beneficiaries = []
    context.available_sdg = []
    context.available_personas = []
    context.available_service_categories = []
    parameters = frappe.form_dict
    context.page = int(parameters.get('page')) if parameters.get('page') else 1
    scope = {}
    filter_sectors = json.loads(parameters['sectors']) if "sectors" in parameters else []
    white_label_domain_sectors = [s["name"] for s in context.available_sectors]
    if len(filter_sectors):
        scope['sectors'] = list(set(white_label_domain_sectors).intersection(filter_sectors))
    else:
        scope['sectors'] = white_label_domain_sectors
    scope['center'] = json.loads(parameters['center']) if parameters.get("center") else [0, 0]
    # For the search we match everything and set limit very high as 
    # we handle pagination locally
    matched = organisation_search.search_index('*', scope=scope, limit=1000000)
    context.start = (context.page - 1) * RESULTS_PER_PAGE
    context.end = context.start + RESULTS_PER_PAGE
    context.total_count = len(matched)
    context.has_next_page = context.total_count > context.end
    context.organisations = [frappe.get_doc('Organisation', d['name']) for d in matched[context.start:context.end]]
    return context
