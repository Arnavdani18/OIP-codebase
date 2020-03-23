import frappe
from contentready_oip import api

def get_context(context):
    if frappe.session.user != 'Guest':
        context.problems = []
        context.user_problems = []
        context.watched_problems = []
        context.problem_contributions = []
        context.solutions = []
        context.user_solutions = []
        context.watched_solutions = []
        context.solution_contributions = []
        dashboard_content = api.get_dashboard_content(limit_page_length=2)
        context.problems = dashboard_content['problems']
        context.solutions = dashboard_content['solutions']
        context.users = dashboard_content['users']
        context.user_problems = dashboard_content['user_problems']
        context.user_solutions = dashboard_content['user_solutions']
        context.watched_problems = dashboard_content['watched_problems']
        context.watched_solutions = dashboard_content['watched_solutions']
        context.problem_contributions = dashboard_content['problem_contributions']
        context.solution_contributions = dashboard_content['solution_contributions']
    else:
        frappe.local.flags.redirect_location = '/'
        raise frappe.Redirect
