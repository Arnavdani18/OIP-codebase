import frappe
from contentready_oip import api

def get_context(context):
    context.problems = api.get_filtered_problems(context.selectedLocation, context.selectedSectors, limit_page_length=5)['problems']
    context.solutions = api.get_filtered_solutions(context.selectedLocation, context.selectedSectors, limit_page_length=5)['solutions']