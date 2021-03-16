import frappe
import json
from contentready_oip import api, user_search

RESULTS_PER_PAGE = 20

def get_context(context):
    context.available_sectors = api.get_available_sectors()
    context.available_beneficiaries = []
    context.available_sdg = []
    context.available_personas = frappe.get_list('Persona', fields=['title','name'])
    parameters = frappe.form_dict
    context.page = int(parameters.get('page')) if parameters.get('page') else 1
    scope = {}
    scope['sectors'] = json.loads(parameters['sectors']) if "sectors" in parameters else []
    scope['sdg'] = json.loads(parameters['sdgs']) if parameters.get("sdgs") else []
    scope['beneficiaries'] = json.loads(parameters['beneficiaries']) if parameters.get("beneficiaries") else []
    scope['personas'] = json.loads(parameters['personas']) if parameters.get("personas") else []
    # For the search we match everything and set limit very high as 
    # we handle pagination locally
    matched = user_search.search_index('*', scope=scope, limit=1000000)
    context.start = (context.page - 1) * RESULTS_PER_PAGE
    context.end = context.start + RESULTS_PER_PAGE
    context.total_count = len(matched)
    context.has_next_page = context.total_count > context.end
    context.users = [frappe.get_doc('User Profile', d['name']) for d in matched[context.start:context.end]]
    return context
