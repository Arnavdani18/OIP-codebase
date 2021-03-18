import frappe
import json
from contentready_oip import api, service_provider_search

RESULTS_PER_PAGE = 20

def get_context(context):
    context.available_sectors = []
    context.available_beneficiaries = []
    context.available_sdg = []
    context.available_personas = []
    context.available_service_categories = frappe.get_list('Service Category', fields=['title','name'])
    parameters = frappe.form_dict
    context.page = int(parameters.get('page')) if parameters.get('page') else 1
    scope = {}
    scope['service_category'] = json.loads(parameters['service_category']) if parameters.get("service_category") else []
    # For the search we match everything and set limit very high as 
    # we handle pagination locally
    matched = service_provider_search.search_index('*', scope=scope, limit=1000000)
    context.start = (context.page - 1) * RESULTS_PER_PAGE
    context.end = context.start + RESULTS_PER_PAGE
    context.total_count = len(matched)
    context.has_next_page = context.total_count > context.end
    context.users = [frappe.get_doc('Service Provider', d['name']) for d in matched[context.start:context.end]]
    return context
