import frappe
from contentready_oip import api

def get_context(context):
    r = api.get_filters()
    context.availableSectors = r['availableSectors']
    if frappe.session.user != 'Guest':
        context.selectedLocation = r['selectedLocation']
        context.selectedSectors = r['selectedSectors']
        context.solutions = api.get_filtered_content('Solution', context.selectedLocation, context.selectedSectors)
