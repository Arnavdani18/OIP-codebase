import frappe
import json
from frappe.utils import get_url
from frappe.utils.html_utils import clean_html
from contentready_oip import api, problem_search, solution_search

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
        p.collaborations_in_progress = api.get_collaborations_in_progress(p.doctype, p.name)
        context.problems.append(p)
    matched = solution_search.search_index('*', scope=scope, limit=RESULTS_PER_PAGE)
    context.solutions = []
    for d in matched:
        p = frappe.get_doc('Solution', d['name'])
        p.collaborations_in_progress = api.get_collaborations_in_progress(p.doctype, p.name)
        context.solutions.append(p)
    oip_configuration = frappe.get_doc('OIP Configuration', '')
    context.slideshow = frappe.as_json(oip_configuration.slideshow)
    context.slideshow_delay = oip_configuration.slideshow_delay
    if len(oip_configuration.slideshow) > 0:
        title = oip_configuration.slideshow[0].heading
        description = clean_html(oip_configuration.slideshow[0].description)
        context.title = title
        context.metatags = {
            "title": title,
            "og:title": title,
            "description": description,
            "og:description": description,
            "og:image": oip_configuration.slideshow[0].image,
        }
    hostname = get_url()
    context.hostname = hostname
    context.domain_settings = frappe.get_doc('OIP White Label Domain', {'url': hostname})
    print("domain_settings",hostname, context.domain_settings)
    return context

