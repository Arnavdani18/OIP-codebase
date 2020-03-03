import frappe
from contentready_oip import api

def get_context(context):
    r = api.get_filters()
    context.selectedLocation = r['selectedLocation']
    context.selectedSectors = r['selectedSectors']
    context.availableSectors = r['availableSectors']
    context.solutions = api.get_filtered_content('Solution', context.selectedLocation, context.selectedSectors)
