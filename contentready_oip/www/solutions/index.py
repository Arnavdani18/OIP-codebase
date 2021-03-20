import frappe
from contentready_oip import api, solution_search
import json

RESULTS_PER_PAGE = 20

def get_context(context):
    # To hide any of these filters, set the available list to an empty list, []
    context.available_sectors = api.get_available_sectors()
    context.available_beneficiaries = []
    # context.available_beneficiaries = frappe.get_list('Beneficiary',fields=['title','name'])
    context.available_sdg = frappe.get_list('Sustainable Development Goal', fields=['title','name'])
    parameters = frappe.form_dict
    context.page = int(parameters.get('page')) if parameters.get('page') else 1
    scope = {}
    scope['sectors'] = json.loads(parameters['sectors']) if "sectors" in parameters else []
    scope['sdg'] = json.loads(parameters['sdgs']) if parameters.get("sdgs") else []
    scope['beneficiaries'] = json.loads(parameters['beneficiaries']) if parameters.get("beneficiaries") else []
    scope['center'] = json.loads(parameters['center']) if parameters.get("center") else [0, 0]
    # For the search we match everything and set limit very high as 
    # we handle pagination locally
    matched = solution_search.search_index('*', scope=scope, limit=1000000)
    context.start = (context.page - 1) * RESULTS_PER_PAGE
    context.end = context.start + RESULTS_PER_PAGE
    context.total_count = len(matched)
    context.has_next_page = context.total_count > context.end
    context.solutions = [frappe.get_doc('Solution', d['name']) for d in matched[context.start:context.end]]
    return context
    
