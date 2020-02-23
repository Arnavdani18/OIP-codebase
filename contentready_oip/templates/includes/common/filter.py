import frappe
import json

@frappe.whitelist(allow_guest = True)
def set_location_filter(selectedLocation=None, distance=25):
    if not 'location_filter' in frappe.session.data or not isinstance(frappe.session.data['location_filter'], dict):
        frappe.session.data['location_filter'] = {}
    selectedLocation = json.loads(selectedLocation)
    distance = int(distance)
    if selectedLocation:
        frappe.session.data['location_filter']['center'] = selectedLocation
    if distance:
        frappe.session.data['location_filter']['distance'] = distance
    return frappe.session.data['location_filter']

@frappe.whitelist(allow_guest = True)
def set_sector_filter(sectors=[]):
    if not 'sector_filter' in frappe.session.data or not isinstance(frappe.session.data['sector_filter'], list):
        frappe.session.data['sector_filter'] = []
    if sectors:
        frappe.session.data['sector_filter'] = json.loads(sectors)
    return frappe.session.data['sector_filter']