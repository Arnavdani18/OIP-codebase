import frappe
from contentready_oip import api

def get_context(context):
    api.create_user_profile_if_missing(None,None,frappe.session.user)
    context.matched_problems = []
    context.matched_solutions = []
    context.matched_contributors = []
    context.available_sectors = api.get_available_sectors()
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
    r = api.get_filtered_paginated_content(context, 'Problem', 'problems')
    context.update(r)
    # print("\n\n\n\n", parameters)
    context.matched_problems = api.get_searched_content('Problem', key)
    # context.matched_problems = context.problems
    # for index, p in enumerate(context.problems):
    #     if p.title.lower().find(key) != -1 or p.description.lower().find(key) != -1:
    #         context.matched_problems.append(p)
    #         for s in p.sectors:
    #             sectors.add(s.sector)
    s = api.get_filtered_paginated_content(context, 'Solution', 'solutions')
    context.update(s)
    context.matched_solutions = api.get_searched_content('Solution', key)
    # for index, p in enumerate(context.solutions):
    #     if p.title.lower().find(key) != -1 or p.description.lower().find(key) != -1:
    #         context.matched_solutions.append(p)
    #         for s in p.sectors:
    #             sectors.add(s.sector)
    context.matched_contributors = api.get_content_recommended_for_user('User Profile', sectors)
    # print('\n\n\n', len(context.matched_problems), len(context.matched_solutions), '\n\n\n')