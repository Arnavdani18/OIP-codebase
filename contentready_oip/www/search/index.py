import frappe
from contentready_oip import api

def get_context(context):
    context.matched_problems = []
    context.matched_solutions = []
    context.matched_contributors = []
    context.key = ''
    parameters = frappe.form_dict
    try:
        key = parameters['key'].lower()
    except:
        key = ''
    if not key:
        return False
    context.key = key
    sectors = set()
    # problems
    context = api.get_content_for_context(context, 'Problem', 'problems')
    # context.matched_problems = context.problems
    for index, p in enumerate(context.problems):
        if p.title.lower().find(key) != -1 or p.description.lower().find(key) != -1:
            context.matched_problems.append(p)
            for s in p.sectors:
                sectors.add(s.sector)
    context = api.get_content_for_context(context, 'Solution', 'solutions')
    for index, p in enumerate(context.solutions):
        if p.title.lower().find(key) != -1 or p.description.lower().find(key) != -1:
            context.matched_solutions.append(p)
            for s in p.sectors:
                sectors.add(s.sector)
    context.matched_contributors = api.get_content_recommended_for_user('User Profile', sectors)
    # print('\n\n\n', len(context.matched_problems), len(context.matched_solutions), '\n\n\n')