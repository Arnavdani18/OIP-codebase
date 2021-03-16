import frappe
from contentready_oip import api, problem_search, solution_search
import json

RESULTS_PER_PAGE = 5

def get_context(context):
    context.full_width = True
    context.stats = api.get_homepage_stats()
    parameters = frappe.form_dict
    scope = {}
    scope['sectors'] = json.loads(parameters['sectors']) if "sectors" in parameters else []
    scope['sdg'] = json.loads(parameters['sdgs']) if parameters.get("sdgs") else []
    scope['beneficiaries'] = json.loads(parameters['beneficiaries']) if parameters.get("beneficiaries") else []
    matched = problem_search.search_index('*', scope=scope, limit=RESULTS_PER_PAGE)
    context.problems = [frappe.get_doc('Problem', d['name']) for d in matched]
    matched = solution_search.search_index('*', scope=scope, limit=RESULTS_PER_PAGE)
    context.solutions = [frappe.get_doc('Solution', d['name']) for d in matched]
    return context
    