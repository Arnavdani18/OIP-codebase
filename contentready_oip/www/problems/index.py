import frappe

def get_context(context):
    selectedLocation = {}
    selectedSectors = []
    if 'location_filter' in frappe.session.data:
        selectedLocation = frappe.session.data.location_filter
    if 'sector_filter' in frappe.session.data:
        selectedSectors = frappe.session.data.sector_filter
    context.selectedLocation = selectedLocation
    context.selectedSectors = selectedSectors
    if 'all' in selectedSectors:
        matching_problems = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': 'Problem'})
    else:
        matching_problems = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': 'Problem', 'sector': ['in', selectedSectors]})
    problem_set = {p['parent'] for p in matching_problems}
    # TODO: Implement location filtering 
    context.problems = []
    for p in problem_set:
        doc = frappe.get_doc('Problem', p)
        doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
        context.problems.append(doc)
    context.availableSectors = frappe.get_list('Sector', ['name', 'title'])