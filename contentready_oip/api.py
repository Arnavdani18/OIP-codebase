import frappe
import json

@frappe.whitelist(allow_guest = True)
def set_location_filter(selectedLocation=None, distance=25):
    if not 'location_filter' in frappe.session.data or not isinstance(frappe.session.data['location_filter'], dict):
        frappe.session.data['location_filter'] = {}
    selectedLocation = json.loads(selectedLocation)
    distance = int(distance)
    if not distance:
        distance = 25
    if selectedLocation:
        frappe.session.data['location_filter']['center'] = selectedLocation
    # if distance:
    frappe.session.data['location_filter']['distance'] = distance
    return frappe.session.data['location_filter']

@frappe.whitelist(allow_guest = True)
def set_sector_filter(sectors=[]):
    if not 'sector_filter' in frappe.session.data or not isinstance(frappe.session.data['sector_filter'], list):
        frappe.session.data['sector_filter'] = []
    if sectors:
        frappe.session.data['sector_filter'] = json.loads(sectors)
    return frappe.session.data['sector_filter']

@frappe.whitelist(allow_guest = True)
def get_filters():
    selectedLocation = {}
    selectedSectors = ['all']
    if 'location_filter' in frappe.session.data:
        selectedLocation = frappe.session.data.location_filter
    if 'sector_filter' in frappe.session.data:
        selectedSectors = frappe.session.data.sector_filter
    availableSectors = frappe.get_list('Sector', ['name', 'title'])
    return {
        'selectedLocation': selectedLocation,
        'selectedSectors': selectedSectors,
        'availableSectors': availableSectors
    }

@frappe.whitelist(allow_guest = True)
def get_filtered_problems(selectedLocation, selectedSectors):
    # TODO: Implement location filtering 
    if 'all' in selectedSectors:
        # matching_problems = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': 'Problem'})
        matching_problems = frappe.get_list('Problem', filters={'is_published': True})
        problem_set = {p['name'] for p in matching_problems}
    else:
        matching_problems = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': 'Problem', 'sector': ['in', selectedSectors]})
        problem_set = {p['parent'] for p in matching_problems}
    problems = []
    for p in problem_set:
        doc = frappe.get_doc('Problem', p)
        if doc.is_published:
            doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
            problems.append(doc)
    
    return {
        'problems': problems,
    }

@frappe.whitelist(allow_guest = True)
def get_similar_problems(text, limit_page_length=5):
    names = frappe.db.get_list('Problem', or_filters={'title': ['like', '%{}%'.format(text)], 'description': ['like', '%{}%'.format(text)]}, limit_page_length=limit_page_length)
    similar_problems = []
    names = {n['name'] for n in names}
    for p in names:
        doc = frappe.get_doc('Problem', p)
        doc.user_image = frappe.get_value('User', doc.owner, 'user_image')
        template = "templates/includes/problems/problem_card.html"
        context = {
            'problem': doc
        }
        html = frappe.render_template(template, context)
        similar_problems.append(html)
    return similar_problems

@frappe.whitelist(allow_guest = True)
def get_orgs_list():
    all_orgs = frappe.get_list('Organisation', fields=['title', 'name'])
    return [{'label': o['title'], 'value': o['name']} for o in all_orgs]

@frappe.whitelist(allow_guest = True)
def get_homepage_stats():
    return {
        'problems': frappe.db.count('Problem', filters={'is_published': True}),
        'solutions': frappe.db.count('Solution', filters={'is_published': True}),
        'collaborators': frappe.db.count('User Profile'),
    }