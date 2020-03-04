import frappe
from contentready_oip import api

def get_context(context):
    r = api.get_filters()
    context.availableSectors = r['availableSectors']
    if frappe.session.user != 'Guest':
        context.selectedLocation = r['selectedLocation']
        context.selectedSectors = r['selectedSectors']
        context.problems = api.get_filtered_content('Problem', context.selectedLocation, context.selectedSectors)
    