import frappe
from contentready_oip import api

def get_context(context):
    context.stats = api.get_homepage_stats()
    r = api.get_filters()
    context.selectedLocation = r['selectedLocation']
    context.selectedSectors = r['selectedSectors']
    context.availableSectors = r['availableSectors']
    context.problems = api.get_filtered_problems(context.selectedLocation, context.selectedSectors, limit_page_length=5)['problems']
    context.solutions = api.get_filtered_solutions(context.selectedLocation, context.selectedSectors, limit_page_length=5)['solutions']