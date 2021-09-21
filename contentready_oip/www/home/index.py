import frappe
from contentready_oip import api, problem_search, solution_search
import json

RESULTS_PER_PAGE = 5

def get_context(context):
    context.full_width = True
    context.stats = api.get_homepage_stats()
    context.partners = api.get_partners()
    parameters = frappe.form_dict
    scope = {}
    scope['sectors'] = json.loads(parameters['sectors']) if "sectors" in parameters else []
    scope['sdg'] = json.loads(parameters['sdgs']) if parameters.get("sdgs") else []
    scope['beneficiaries'] = json.loads(parameters['beneficiaries']) if parameters.get("beneficiaries") else []
    matched = problem_search.search_index('*', scope=scope, limit=RESULTS_PER_PAGE)
    context.problems = []
    for d in matched:
        p = frappe.get_doc('Problem', d['name'])
        p.collaboration_in_progress = api.is_collaboration_in_progress(p.doctype, p.name)
        context.problems.append(p)
    matched = solution_search.search_index('*', scope=scope, limit=RESULTS_PER_PAGE)
    context.solutions = []
    for d in matched:
        p = frappe.get_doc('Solution', d['name'])
        p.collaboration_in_progress = api.is_collaboration_in_progress(p.doctype, p.name)
        context.solutions.append(p)
    oip_configuration = frappe.get_doc('OIP Configuration', '')
    context.slideshow = frappe.as_json(oip_configuration.slideshow)
    context.slideshow_delay = oip_configuration.slideshow_delay
    return context
    