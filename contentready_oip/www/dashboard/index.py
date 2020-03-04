import frappe
from contentready_oip import api

def get_context(context):
    print(frappe.session.user)
    if frappe.session.user != 'Guest':
        interesting_content = api.get_interesting_content()
        context.problems = interesting_content['problems']
        context.solutions = interesting_content['solutions']
        context.users = interesting_content['users']
        context.user_problems = interesting_content['user_problems']
        context.user_solutions = interesting_content['user_solutions']
        context.watched_problems = interesting_content['watched_problems']
        context.watched_solutions = interesting_content['watched_solutions']
    else:
        frappe.local.flags.redirect_location = '/'
        raise frappe.Redirect