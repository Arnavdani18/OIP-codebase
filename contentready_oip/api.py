import frappe
import json
from frappe import _
import platform
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, Object
from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q
from frappe.email.doctype.email_template.email_template import get_email_template
import meilisearch

python_version_2 = platform.python_version().startswith('2')
CLIENT = meilisearch.Client('http://localhost:7700/', 'test123')

def nudge_guests():
    if not frappe.session.user or frappe.session.user == 'Guest':
        frappe.throw('Please login to collaborate.')

def create_user_profile_if_missing(doc=None, event_name=None, email=None):
    try:
        if email == 'Guest':
            return False
        if email:
            doc = frappe.get_doc('User', email)
        if not frappe.db.exists('User Profile', doc.email):
            profile = frappe.get_doc({
                'doctype': 'User Profile',
                'user': doc.email,
                'owner': doc.email
            })
            profile.save()
            frappe.db.commit()
    except Exception as e:
        print(str(e))

@frappe.whitelist(allow_guest = True)
def set_location_filter(filter_location_name=None, filter_location_lat=None,filter_location_lng=None, filter_location_range=25):
    if filter_location_name != None:
        frappe.session.data['filter_location_name'] = filter_location_name
    if filter_location_lat != None:
        frappe.session.data['filter_location_lat'] = float(filter_location_lat)
    if filter_location_lng != None:
        frappe.session.data['filter_location_lng'] = float(filter_location_lng)
    if filter_location_range != None:
        frappe.session.data['filter_location_range'] = int(filter_location_range)
    return filter_location_lat, filter_location_lng, filter_location_range

@frappe.whitelist(allow_guest = True)
def clear_location_filter():
    frappe.session.data['filter_location_name'] = ''
    frappe.session.data['filter_location_lat'] = None
    frappe.session.data['filter_location_lng'] = None
    frappe.session.data['filter_location_range'] = None
    return True


@frappe.whitelist(allow_guest = True)
def set_sector_filter(filter_sectors=[]):
    if not isinstance(filter_sectors, list):
        filter_sectors = json.loads(filter_sectors)
    if not filter_sectors:
        filter_sectors = ['all']
    frappe.session.data['filter_sectors'] = filter_sectors
    return frappe.session.data['filter_sectors']

@frappe.whitelist(allow_guest = True)
def get_available_sectors():
    hostname = get_url()
    try:
        domain = frappe.get_doc('OIP White Label Domain', {'url': hostname})
        sectors = [{'name': s.sector, 'title': s.sector_title} for s in domain.sectors]
        assert len(sectors) > 0, 'Need at least 1 sector per domain. Reverting to defaults.'
        return sectors
    except Exception as e:
        print(str(e))
        return frappe.get_list('Sector', ['name', 'title'])

@frappe.whitelist(allow_guest = True)
def get_partners():
    hostname = get_url()
    try:
        domain = frappe.get_doc('OIP White Label Domain', {'url': hostname})
        partners = [{'brandmark': p.brandmark,'url': p.url, 'title': p.title} for p in domain.partners]
        return partners
    except Exception as e:
        print(str(e))

@frappe.whitelist(allow_guest = True)
def get_domain_theme():
    hostname = get_url()
    theme_url = ''
    try:
        assert True==False, 'Impossible'
    except Exception as e:
        print(str(e))
        default_theme = frappe.get_value('Website Settings','', 'website_theme')
        if default_theme:
            theme_url = frappe.get_value('Website Theme', default_theme, 'theme_url')
    return theme_url

@frappe.whitelist(allow_guest = True)
def get_url():
    return frappe.utils.get_host_name_from_request()

@frappe.whitelist(allow_guest = True)
def get_filters():
    filter_sectors = ['all']
    filter_location_name = ''
    filter_location_lat = None
    filter_location_lng = None
    filter_location_range = None
    if 'filter_location_name' in frappe.session.data:
        filter_location_name = frappe.session.data.filter_location_name
    if 'filter_location_lat' in frappe.session.data:
        filter_location_lat = frappe.session.data.filter_location_lat
    if 'filter_location_lng' in frappe.session.data:
        filter_location_lng = frappe.session.data.filter_location_lng
    if 'filter_location_range' in frappe.session.data:
        filter_location_range = frappe.session.data.filter_location_range
    if 'filter_sectors' in frappe.session.data:
        filter_sectors = frappe.session.data.filter_sectors
    available_sectors = get_available_sectors()
    return {
        'filter_location_name': filter_location_name,
        'filter_location_lat': filter_location_lat,
        'filter_location_lng': filter_location_lng,
        'filter_location_range': filter_location_range,
        'filter_sectors': filter_sectors,
        'available_sectors': available_sectors
    }

@frappe.whitelist(allow_guest = True)
def get_doc_by_type_name(doctype, name):
    return frappe.get_doc(doctype, name)

@frappe.whitelist(allow_guest = True)
def get_all_doc(doctype):
    doc_list = frappe.get_list(doctype)
    doc = []
    for doc_name in doc_list:
        d = frappe.get_doc(doctype,doc_name['name'])
        if d.is_published:
            doc.append(d)

    return doc

@frappe.whitelist(allow_guest = True)
def get_doc_field(doctype, name, field):
    try:
        field = json.loads(field)
    except:
        field = field

    return frappe.get_value(doctype, name, field)

@frappe.whitelist(allow_guest = True)
def get_child_table(child_table_doctype, parent_doctype, parent_name):
    return frappe.get_all(child_table_doctype, filters={'parenttype': parent_doctype, 'parent': parent_name})

def convert_if_json(value):
    cmp_type = str
    if python_version_2:
        cmp_type = basestring
    if isinstance(value, cmp_type):
        value = json.loads(value)
    return value

def get_filtered_paginated_content(context, doctype, key, limit_page_length=20):
    payload = {}
    try:
        payload['available_sectors'] = get_available_sectors()
        parameters = frappe.form_dict
        # page
        try:
            payload['page'] = int(parameters['page'])
        except:
            payload['page'] = 1
        limit_start = payload['page'] - 1
        # limit_page_length = 20
        if doctype == 'User Profile':
            parameters = frappe.form_dict
            try:
                filter_sectors = json.loads(parameters['sectors'])
            except Exception as e:
                filter_sectors = ['all']
                # filter_sectors = []
            filtered_content = get_content_recommended_for_user('User Profile', filter_sectors, limit_page_length=limit_page_length)
            # filtered_content = search_contributors_by_text('', limit_page_length=200, html=False)
        else:
            filtered_content = get_filtered_content(doctype)
        payload['start'] = limit_start*limit_page_length
        payload['end'] = payload['start'] + limit_page_length
        payload['total_count'] = len(filtered_content)
        if payload['end'] > payload['total_count']:
            payload['end'] = payload['total_count']
        payload['has_next_page'] = False
        if payload['total_count'] > limit_page_length*payload['page']:
            payload['has_next_page'] = True
        payload[key] = filtered_content[payload['start']:payload['end']]
    except Exception as e:
        print(str(e))
    return payload


@frappe.whitelist(allow_guest = True)
def get_filtered_content(doctype):
    content = []
    try:
        parameters = frappe.form_dict
        # filter_location_name
        try:
            filter_location_name = parameters['loc']
        except:
            filter_location_name = None
        # filter_location_lat
        try:
            filter_location_lat = float(parameters['lat'])
        except:
            filter_location_lat = None
        # filter_location_lng
        try:
            filter_location_lng = float(parameters['lng'])
        except:
            filter_location_lng = None
        # filter_location_range
        try:
            filter_location_range = int(parameters['rng'])
        except:
            filter_location_range = None
        # filter_sectors
        try:
            filter_sectors = json.loads(parameters['sectors'])
        except Exception as e:
            # filter_sectors = ['all']
            filter_sectors = []
        # if not filter_sectors:
            # filter_sectors = ['all']
        # print('\n\n\n', filter_sectors, len(filter_sectors), '\n\n\n')
        if 'all' in filter_sectors:
            available_sectors = get_available_sectors()
            filter_sectors = {a['name'] for a in available_sectors}
        filtered = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': doctype, 'sector': ['in', filter_sectors]})
        content_set = {f['parent'] for f in filtered}
        try:
            user = frappe.get_doc('User Profile', frappe.session.user)
            user_sectors = {sector.sector for sector in user.sectors}
        except:
            user_sectors = set()
        # TODO: Implement location filtering using Elasticsearch
        from geopy import distance
        for c in content_set:
            try:
                doc = frappe.get_doc(doctype, c)
                if doc.is_published:
                    if (doc.latitude != None) and (doc.longitude != None) and (filter_location_lat != None) and (filter_location_lng != None) and (filter_location_range != None):
                        distance_km = distance.distance((filter_location_lat, filter_location_lng), (float(doc.latitude), float(doc.longitude))).km
                        if distance_km > filter_location_range:
                            # skip this document as it's outside our bounds
                            continue
                    doc_sectors = {sector.sector for sector in doc.sectors}
                    relevant_sectors = doc_sectors.intersection(user_sectors)
                    if doctype == 'Problem':
                        doc.score = 0.3 * len(doc.validations) + 0.1 * len(doc.likes) + 0.1 * len(doc.enrichments) + 0.1 * len(doc.watchers) + 0.05 * len(doc.discussions) + 0.3 * len(relevant_sectors)
                    else:
                        doc.score = 0.3 * len(doc.validations) + 0.1 * len(doc.likes) + 0.1 * len(doc.watchers) + 0.05 * len(doc.discussions) + 0.3 * len(relevant_sectors)
                    content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    content.sort(key=lambda x: x.score, reverse=True)
    return content

@frappe.whitelist(allow_guest = True)
def search_content_by_text(doctype, text, limit_page_length=5, html=True):
    content = []
    try:
        names = frappe.db.get_list(doctype, or_filters={'title': ['like', '%{}%'.format(text)], 'description': ['like', '%{}%'.format(text)]}, filters={'is_published': True}, limit_page_length=limit_page_length)
        names = {n['name'] for n in names}
        for p in names:
            try:
                doc = frappe.get_doc(doctype, p)
                doc.photo = frappe.get_value('User Profile', doc.owner, 'photo')
                if html:
                    content_type = doctype.lower()
                    template = "templates/includes/{}/{}_card.html".format(content_type, content_type)
                    context = {
                        content_type: doc
                    }
                    html = frappe.render_template(template, context)
                    content.append(html)
                else:
                    content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content

@frappe.whitelist(allow_guest = True)
def global_search_content_by_text(text, limit_page_length=5, html=True):
    sectors = set()
    payload = {}
    try:
        for doctype in ['Problem', 'Solution']:
            payload[doctype] = []
            content = search_content_by_text(doctype, text, limit_page_length, html=False)
            for c in content:
                content_type = doctype.lower()
                template = "templates/includes/{}/{}_card.html".format(content_type, content_type)
                context = {
                    content_type: c
                }
                html = frappe.render_template(template, context)
                payload[doctype].append(html)
                for s in c.sectors:
                    sectors.add(s.sector)
        contributors = get_content_recommended_for_user('User Profile', sectors, limit_page_length=limit_page_length)
        doctype = 'User Profile'
        payload[doctype] = []
        for c in contributors:
            template = "templates/includes/common/user_card.html"
            context = {
                'user': c
            }
            html = frappe.render_template(template, context)
            payload[doctype].append(html)
    except Exception as e:
        print(str(e))
    return payload

@frappe.whitelist(allow_guest = True)
def search_contributors_by_text(text, limit_page_length=5, html=True):
    content = []
    try:
        doctype = 'User Profile'
        names = frappe.db.get_list(doctype, or_filters={'full_name': ['like', '%{}%'.format(text)]}, limit_page_length=limit_page_length)
        names = {n['name'] for n in names}
        for p in names:
            try:
                doc = frappe.get_doc(doctype, p)
                doc.photo = frappe.get_value('User Profile', doc.owner, 'photo')
                if html:
                    template = "templates/includes/common/user_card.html"
                    context = {
                        'user': doc
                    }
                    html = frappe.render_template(template, context)
                    content.append(html)
                else:
                    content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content

@frappe.whitelist(allow_guest = True)
def get_orgs_list():
    all_orgs = frappe.get_list('Organisation', fields=['title', 'name'])
    return [{'label': o['title'], 'value': o['name']} for o in all_orgs]

@frappe.whitelist(allow_guest = True)
def get_sdg_list():
    sdgs = frappe.get_list('Sustainable Development Goal', fields=['title','name'])
    return [{'label': o['title'], 'value': o['name']} for o in sdgs]

@frappe.whitelist(allow_guest = False)
def get_user_list():
    all_users = frappe.get_list('User Profile', filters={'user': ['not in', ['Guest', 'Administrator']]}, fields=['full_name', 'user'])
    return [{'text': o['full_name'], 'id': o['user']} for o in all_users]

@frappe.whitelist(allow_guest = True)
def get_persona_list():
    all_personas = frappe.get_list('Persona', fields=['title', 'name'])
    return [{'label': o['title'], 'value': o['name']} for o in all_personas]

@frappe.whitelist(allow_guest = True)
def get_sector_list():
    available_sectors = get_available_sectors()
    # all_sectors = frappe.get_list('Sector', fields=['title', 'name'])
    return [{'label': o['title'], 'value': o['name']} for o in available_sectors]

@frappe.whitelist(allow_guest = True)
def get_homepage_stats():
    return {
        'problems': frappe.db.count('Problem', filters={'is_published': True}),
        'solutions': frappe.db.count('Solution', filters={'is_published': True}),
        'collaborators': frappe.db.count('User Profile'),
    }

@frappe.whitelist(allow_guest = True)
def has_user_contributed(child_doctype, parent_doctype, parent_name):
    contributions_by_user = frappe.db.count(child_doctype, filters={'user': frappe.session.user, 'parenttype': parent_doctype, 'parent': parent_name})
    return contributions_by_user > 0

@frappe.whitelist(allow_guest = True)
def can_user_contribute(child_doctype, parent_doctype, parent_name):
    doc_owner = frappe.get_value(parent_doctype, parent_name, 'owner')
    # print(doc_owner, frappe.session.user)
    return has_user_contributed(child_doctype, parent_doctype, parent_name), doc_owner == frappe.session.user

@frappe.whitelist(allow_guest = False)
def toggle_contribution(child_doctype, parent_doctype, parent_name, field_name):
    nudge_guests()
    contributions = frappe.get_all(child_doctype, filters={'user': frappe.session.user, 'parenttype': parent_doctype, 'parent': parent_name})
    if len(contributions) > 0:
        # user has already contributed to this document
        for c in contributions:
            frappe.delete_doc(child_doctype, c['name'])
    else:
        # add contribution for user
        doc = frappe.get_doc(parent_doctype, parent_name)
        like = doc.append(field_name, {})
        like.user = frappe.session.user
        doc.save()
        frappe.db.commit()
    return has_user_contributed(child_doctype, parent_doctype, parent_name), get_child_table(child_doctype, parent_doctype, parent_name)

@frappe.whitelist(allow_guest = False)
def add_comment(doctype, name, text, media=None, html=True):
    doc = frappe.get_doc({
        'doctype': 'Discussion',
        'text': text,
        'user': frappe.session.user,
        'parent_doctype': doctype,
        'parent_name': name
    })
    media = json.loads(media)
    for f in media:
        a = doc.append('media', {})
        a.attachment = f
    doc.save()
    parent_doc = frappe.get_doc(doctype, name)
    if doctype == 'Discussion':
        child = parent_doc.append('replies', {})
    else:
        child = parent_doc.append('discussions', {})
    child.discussion = doc.name
    parent_doc.save()
    frappe.db.commit()
    if html:
        template = "templates/includes/common/comment.html"
        context = {
            'comment': doc
        }
        html = frappe.render_template(template, context)
        return html
    else:
        return doc

@frappe.whitelist(allow_guest = False)
def get_problem_detail_modal(name, html=True):
    # Get problem detail modal on add solution and edit solution.
    # { param: string } eg. 'Problem001'
    doc = frappe.get_doc('Problem',name)
    if html:
        detail_modal_template = "templates/includes/solution/problem_detail_modal.html"
        detail_modal = frappe.render_template(detail_modal_template,doc.as_dict())
        
        enrichment_list = [e.as_dict() for e in doc.enrichments ]
        return (detail_modal,enrichment_list)
    else:
        return doc

@frappe.whitelist(allow_guest = False)
def get_problem_card(name, html=True):
    doc = frappe.get_doc('Problem', name)
    if html:
        context = {
            'problem': doc
        }
        problem_card_template = "templates/includes/problem/problem_card.html"
        overview_tab_template = "templates/includes/problem/overview.html"

        problem_card = frappe.render_template(problem_card_template, context)
        overview_tab = frappe.render_template(overview_tab_template,doc.as_dict())
        return problem_card, doc.name,overview_tab
    else:
        return doc

@frappe.whitelist(allow_guest = False)
def get_problem_details(name):
    doc = frappe.get_doc('Problem', name)
    return doc

@frappe.whitelist(allow_guest = False)
def get_problem_overview(name, html=True):
    doc = frappe.get_doc('Problem', name)
    if html:
        context = {
            'problem': doc
        }
        template = "templates/includes/problem/problem_card.html"
        html = frappe.render_template(template, context)
        context = doc.as_dict()
        template = "templates/includes/problem/overview.html"
        html += '<div style="background-color: white;">' + frappe.render_template(template, context) + '</div>'
        return html, doc.name
    else:
        return doc

@frappe.whitelist(allow_guest = False)
def add_primary_content(doctype, doc, is_draft=False):
    doc = json.loads(doc)
    if isinstance(is_draft,str):
        is_draft = json.loads(is_draft)
    if 'name' in doc and doc['name']:
        # edit
        content = frappe.get_doc(doctype, doc['name'])
        content.update(doc)
        content.flags.ignore_mandatory = is_draft
        content.save()
    else:
        # create
        content = frappe.get_doc({
            'doctype': doctype
        })
        content.update(doc)
        content.insert(ignore_mandatory=is_draft)
    frappe.db.commit()
    content = frappe.get_doc(doctype, content.name)
    return content


@frappe.whitelist(allow_guest = False)
def add_enrichment(doc,is_draft=False):
    doc = json.loads(doc)
    if isinstance(is_draft,str):
        is_draft = json.loads(is_draft)
    if not ('problem' in doc or doc['problem']):
        return False
    doctype = 'Enrichment'
    if 'name' in doc and doc['name']:
        # edit
        content = frappe.get_doc(doctype, doc['name'])
        content.update(doc)
        content.flags.ignore_mandatory = is_draft
        content.save()
    else:
        # create
        if has_user_contributed('Enrichment Table', 'Problem', doc['problem']):
            frappe.throw('You have already enriched this problem.')
        content = frappe.get_doc({
            'doctype': doctype
        })
        content.update(doc)
        content.insert(ignore_mandatory=is_draft)
    frappe.db.commit()
    content = frappe.get_doc(doctype, content.name)
    route = frappe.get_value('Problem', content.problem, 'route')
    return content, route

@frappe.whitelist(allow_guest = False)
def add_or_edit_validation(doctype, name, validation, html=True):
    validation = json.loads(validation)
    if doctype == 'Validation Table':
        # in edit mode
        v = frappe.get_doc('Validation Table', name)
        v.update(validation)
        v.save()
        total_count = frappe.db.count('Validation Table', filters={'parenttype': v.parenttype, 'parent': v.parent})
    else:
        if has_user_contributed('Validation Table', doctype, name):
            frappe.throw('You have already validated this {}.'.format(doctype).capitalize())
        doc = frappe.get_doc(doctype, name)
        v = doc.append('validations', {})
        v.update(validation)
        doc.save()
        total_count = frappe.db.count('Validation Table', filters={'parenttype': doctype, 'parent': name})
    frappe.db.commit()
    if html:
        context = {
            'validation': v
        }
        template = "templates/includes/common/validation_card.html"
        html = frappe.render_template(template, context)
        return html, total_count
    else:
        return doc

@frappe.whitelist(allow_guest = False)
def add_or_edit_collaboration(doctype, name, collaboration, html=True):
    collaboration = json.loads(collaboration)
    print(collaboration)
    if doctype == 'Collaboration Intent':
        # in edit mode
        doc = frappe.get_doc('Collaboration Intent', name)
        doc.comment = collaboration['comment']
        doc.personas = []
        doc.personas_list = ','.join(collaboration['personas'])
        for p in collaboration['personas']:
            row = doc.append('personas', {})
            row.persona = p
        doc.save()
        total_count = frappe.db.count('Collaboration Table', filters={'parenttype': doc.parent_doctype, 'parent': doc.parent_name})
    else:
        # creating new collaboration
        if has_user_contributed('Collaboration Table', doctype, name):
            frappe.throw('You have already added your collaboration intent on this {}.'.format(doctype).capitalize())
        doc = frappe.get_doc({
            'doctype': 'Collaboration Intent',
            'comment': collaboration['comment'],
            'user': frappe.session.user,
            'parent_doctype': doctype,
            'parent_name': name
        })
        for p in collaboration['personas']:
            row = doc.append('personas', {})
            row.persona = p
        doc.save()
        parent_doc = frappe.get_doc(doctype, name)
        child = parent_doc.append('collaborations', {})
        child.collaboration_intent = doc.name
        parent_doc.save()
        frappe.db.commit()
        total_count = frappe.db.count('Collaboration Table', filters={'parenttype': doctype, 'parent': name})
    frappe.db.commit()
    if html:
        context = {
            'collaboration': doc,
            'personas': get_persona_list()
        }
        template = "templates/includes/common/collaboration_card.html"
        html = frappe.render_template(template, context)
        return html, total_count
    else:
        return doc

@frappe.whitelist(allow_guest = True)
def add_subscriber(email, first_name='', last_name=''):
    contact = frappe.get_doc({
        'doctype': 'OIP Contact',
        'email': email,
        'first_name': first_name,
        'last_name': last_name
    })
    contact.insert()
    frappe.db.commit()
    r = get_email_template('New Subscriber', {})
    frappe.sendmail([email], subject=r['subject'], message=r['message'], delayed=True)
    return True

@frappe.whitelist(allow_guest = True)
def unsubscribe_email(email):
    try:
        contact = frappe.get_doc('OIP Contact', {'email':email})
        contact.is_unsubscribed = True
        contact.save()
        frappe.db.commit()
        success_msg = 'You have been unsubscribed from our emails.'
        frappe.respond_as_web_page(_("Unsubscribe Successful"),
                                    _(success_msg),                 
                                    http_status_code=200, indicator_color='green', fullpage=True, primary_action='/')
        return frappe.website.render.render("message", http_status_code=200)
    except Exception as e:
        print(str(e))
        error_msg = 'Error while unsubscribing. {}'.format(str(e))
        frappe.respond_as_web_page(_("Unsubscribe Unsuccessful"),
                                    _(error_msg),                 
                                    http_status_code=503, indicator_color='red', fullpage=True, primary_action='/')
        return frappe.website.render.render("message", http_status_code=503)


@frappe.whitelist(allow_guest = False)
def get_content_by_user(doctype, limit_page_length=5):
    content = []
    try:
        filtered = frappe.get_list(doctype, filters={'owner': frappe.session.user, 'is_published': True}, limit_page_length=limit_page_length)
        for f in filtered:
            try:
                doc = frappe.get_doc(doctype, f['name'])
                if doc.is_published:
                    content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content

@frappe.whitelist(allow_guest = False)
def get_contributions_by_user(parent_doctype, child_doctypes, limit_page_length=5):
    # content_set = set()
    content = []
    try:
        content_dict = {}
        for child_doctype in child_doctypes:
            filtered = frappe.get_list(child_doctype, fields=['parent', 'modified'], filters={'user': frappe.session.user, 'parenttype': parent_doctype})
            for f in filtered:
                if f['parent'] not in content_dict:
                    content_dict[f['parent']] = []
                content_dict[f['parent']].append({'type': child_doctype, 'modified': f['modified']})
                # content_set.add(f['parent'])
        content = []
        # print(content_dict)
        # for c in content_set:
        for c in content_dict:
            try:
                doc = frappe.get_doc(parent_doctype, c)
                if doc.is_published:
                    doc.enriched = False
                    doc.validated = False
                    doc.collaborated = False
                    doc.discussed = False
                    for e in content_dict[c]:
                        contribution_type = e['type']
                        if contribution_type == 'Enrichment Table':
                            doc.enriched = e['modified']
                        elif contribution_type == 'Validation Table':
                            doc.validated = e['modified']
                        elif contribution_type == 'Collaboration Table':
                            doc.collaborated = e['modified']
                        elif contribution_type == 'Discussion Table':
                            doc.discussed = e['modified']
                    content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content

@frappe.whitelist(allow_guest = False)
def get_content_watched_by_user(doctype, limit_page_length=5):
    content = []
    try:
        filtered = frappe.get_list('Watch Table', fields=['parent'], filters={'parenttype': doctype, 'user': frappe.session.user}, limit_page_length=limit_page_length)
        content_set = {f['parent'] for f in filtered}
        for c in content_set:
            try:
                doc = frappe.get_doc(doctype, c)
                if doc.is_published:
                    content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content

@frappe.whitelist(allow_guest = False)
def get_content_recommended_for_user(doctype, sectors, limit_page_length=5,creation=None,html=False):
    content = []
    try:
        if creation:
            filtered = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': doctype, 'sector': ['in', sectors], 'owner': ['!=', frappe.session.user], 'creation': ['>=',creation]})
            content_set = {f['parent'] for f in filtered}
        else:
            if 'all' in sectors:
                filtered = frappe.get_list(doctype, filters={'owner': ['!=', frappe.session.user]})
                content_set = {f['name'] for f in filtered}
            else:
                filtered = frappe.get_list('Sector Table', fields=['parent'], filters={'parenttype': doctype, 'sector': ['in', sectors], 'owner': ['!=', frappe.session.user]})
                content_set = {f['parent'] for f in filtered}
        for c in content_set:
            try:
                doc = frappe.get_doc(doctype, c)
                # don't show content that the user has already contributed to
                if doc.is_published and not has_user_contributed('Like Table', doctype, c) and not has_user_contributed('Watch Table',doctype, c) and not has_user_contributed('Validation Table',doctype, c) and not has_user_contributed('Collaboration Table',doctype, c) and not has_user_contributed('Enrichment Table',doctype, c):
                    doc.photo = frappe.get_value('User Profile', doc.owner, 'photo')
                    if html:
                        if doctype == 'Problem':
                            context = {
                                'problem': doc
                            }
                            template = "templates/includes/problem/problem_card.html"
                        elif doctype == 'Solution':
                            context = {
                                'solution': doc
                            }
                            template = "templates/includes/solution/solution_card.html"
                        elif doctype == 'User Profile':
                            context = {
                                'user': doc
                            }
                            template = "templates/includes/common/user_card.html"
                        html = frappe.render_template(template, context)
                        content.append(html)
                    else:
                        content.append(doc)
            except Exception as e:
                print(str(e))
    except Exception as e:
        print(str(e))
    return content

@frappe.whitelist(allow_guest = False)
def get_drafts_by_user(doctypes=None, limit_page_length=5):
    content = []
    if not doctypes:
        doctypes = ['Problem', 'Solution', 'Enrichment']
    try:
        for doctype in doctypes:
            filtered = frappe.get_list(doctype, filters={'is_published': False, 'owner': frappe.session.user})
            content_set = {f['name'] for f in filtered}
            for c in content_set:
                try:
                    doc = frappe.get_doc(doctype, c)
                    doc.photo = frappe.get_value('User Profile', doc.owner, 'photo')
                    content.append(doc)
                except Exception as e:
                    print(str(e))
    except Exception as e:
        print(str(e))
    print("\n\n\nDrafts",content)
    return content

@frappe.whitelist(allow_guest = False)
def get_dashboard_content(limit_page_length=5,content_list=None):
    if not content_list:
        content_list = [
            'recommended_problems',
            'recommended_solutions',
            'recommended_users',
            'user_problems',
            'user_solutions',
            'watched_problems',
            'watched_solutions',
            'contributed_problems',
            'contributed_solutions',
            'drafts',
            'self_profile'
        ]
    try:
        user = frappe.get_doc('User Profile', frappe.session.user)
        sectors = [sector.sector for sector in user.sectors]
    except:
        sectors = []
        # frappe.throw('Please create your user profile to personalise this page')
    payload = {}
    if 'recommended_problems' in content_list:
        payload['recommended_problems'] = get_content_recommended_for_user('Problem', sectors, limit_page_length=limit_page_length)
    if 'recommended_solutions' in content_list:
        payload['recommended_solutions'] = get_content_recommended_for_user('Solution', sectors, limit_page_length=limit_page_length)
    if 'recommended_users' in content_list:
        payload['recommended_users'] = get_content_recommended_for_user('User Profile', sectors, limit_page_length=limit_page_length)
    if 'user_problems' in content_list:
        payload['user_problems'] = get_content_by_user('Problem', limit_page_length=limit_page_length)
    if 'user_solutions' in content_list:
        payload['user_solutions'] = get_content_by_user('Solution', limit_page_length=limit_page_length)
    if 'self_profile' in content_list:
        payload['self_profile'] = frappe.get_doc('User Profile', frappe.session.user).as_dict()
    if 'watched_problems' in content_list:
        payload['watched_problems'] = get_content_watched_by_user('Problem', limit_page_length=limit_page_length)
    if 'watched_solutions' in content_list:
        payload['watched_solutions'] = get_content_watched_by_user('Solution', limit_page_length=limit_page_length)
    if 'contributed_problems' in content_list:
        payload['contributed_problems'] = get_contributions_by_user('Problem', ['Enrichment Table', 'Validation Table', 'Collaboration Table', 'Discussion Table'], limit_page_length=limit_page_length)
    if 'contributed_solutions' in content_list:
        payload['contributed_solutions'] = get_contributions_by_user('Solution', ['Validation Table', 'Collaboration Table', 'Discussion Table'], limit_page_length=limit_page_length)
    if 'drafts' in content_list:
        payload['drafts'] = get_drafts_by_user(limit_page_length=limit_page_length)
    return payload

@frappe.whitelist(allow_guest = False)
def delete_contribution(child_doctype, name):
    try:
        frappe.delete_doc(child_doctype, name)
        return True
    except:
        frappe.throw('{} not found in {}.'.format(name, child_doctype))

@frappe.whitelist(allow_guest = False)
def delete_collaboration(name):
    try:
        e = frappe.get_doc('Collaboration Table', {'collaboration_intent': name})
        # delete from the parent child table
        frappe.delete_doc('Collaboration Table', e.name)
        # delete the primary document
        frappe.delete_doc('Collaboration Intent', name)
        return True
    except:
        frappe.throw('Collaboration not found.')

@frappe.whitelist(allow_guest = False)
def delete_reply(reply):
    try:
        reply = json.loads(reply)
        
        # delete from the parent child table
        frappe.delete_doc_if_exists('Discussion Table', reply['name'])
        # delete the primary document
        frappe.delete_doc_if_exists('Discussion', reply['discussion'])
        frappe.db.commit()
        return True
    except:
        frappe.throw('Discussion not found.')

@frappe.whitelist(allow_guest = False)
def delete_enrichment(name):
    try:
        e = frappe.get_doc('Enrichment Table', {'enrichment': name})
        # delete from the problem child table
        frappe.delete_doc('Enrichment Table', e.name)
        # delete the primary document
        frappe.delete_doc('Enrichment', name)
        return True
    except:
        frappe.throw('Enrichment not found.')

@frappe.whitelist(allow_guest=True)
def register(form=None):
    if not form:
        form = dict(frappe.form_dict)
    frappe.set_user('Administrator')
    form['doctype'] = 'User'
    user_by_email = frappe.db.get("User", {"email": form['email']})
    if not user_by_email:
        from frappe.utils import random_string
        user = frappe.get_doc({
            "doctype":"User",
            "email": form['email'],
            "first_name": form['first_name'],
            "last_name": form['last_name'],
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": False
        })
        user.flags.ignore_permissions = True
        user.insert()
        # set default signup role as per Portal Settings
        default_role = frappe.db.get_value("Portal Settings", None, "default_role")
        if default_role:
            user.add_roles(default_role)
        frappe.db.commit()
        success_msg = "You will shortly receive a verification email with a link to set your password and start the application process."
        frappe.respond_as_web_page(_("Sign up successful"),
            _(success_msg),
            http_status_code=200, indicator_color='green', fullpage = True, primary_action='/')
        return frappe.website.render.render("message", http_status_code=200)
    else:
        error_msg = 'You have already signed up with this email. Try logging in instead.'
        # frappe.throw(error_msg)
        frappe.respond_as_web_page(_("Sign up error"),
            _(error_msg),
            http_status_code=400, indicator_color='red', fullpage = True, primary_action='/')
        return frappe.website.render.render("message", http_status_code=400)

@frappe.whitelist(allow_guest=False)
def set_notification_as_read(notification_name):
    frappe.set_value('OIP Notification', notification_name, 'is_read', True)
    return True

@frappe.whitelist(allow_guest=True)
def complete_linkedin_login(code, state):
    from frappe.integrations.oauth2_logins import decoder_compat
    from frappe.utils import oauth
    oauth2_providers = oauth.get_oauth2_providers()
    provider = 'linkedin'
    flow = oauth.get_oauth2_flow(provider)
    args = {
        "data": {
            "code": code,
            "redirect_uri": oauth.get_redirect_uri(provider),
            "grant_type": "authorization_code",
        },
        "decoder": decoder_compat
    }
    session = flow.get_auth_session(**args)
    api_endpoint = oauth2_providers[provider].get("api_endpoint")
    api_endpoint_args = oauth2_providers[provider].get("api_endpoint_args")
    info = session.get(api_endpoint, params=api_endpoint_args).json()
    profile_endpoint = 'https://api.linkedin.com/v2/me'
    profile_params = {'projection':'(id,firstName,lastName,profilePicture(displayImage~:playableStreams))'}
    profile = session.get(profile_endpoint, params=profile_params).json()
    info = unpack_linkedin_response(info, profile)
    if not (info.get("email_verified") or info.get("email")):
        frappe.throw(_("Email not verified with {0}").format(provider.title()))
    oauth.login_oauth_user(info, provider=provider, state=state)
    # print('once logged in, we create the profile')
    doc = frappe.get_doc('User', info.get('email'))
    # create user profile because social login does not seem to trigger frappe hook
    create_user_profile_if_missing(doc, 'social_login')

def unpack_linkedin_response(info, profile=None):
    # print(profile)
    # print(info)
    # info = {'elements': [{'handle~': {'emailAddress': 'tej@iotready.co'}, 'handle': 'urn:li:emailAddress:7957229897'}]}
    payload = {}
    payload['email'] = info['elements'][0]['handle~']['emailAddress']
    payload['handle'] = info['elements'][0]['handle']
    if not profile:
        # needs a second API call to get name info, we should save the user even if that fails
        payload['first_name'] = payload['email']
    else:
        import requests
        lang = list(profile['firstName']['localized'].keys())[0]
        payload['first_name'] = profile['firstName']['localized'][lang]
        payload['last_name'] = profile['lastName']['localized'][lang]
        # The last element of the pictures array is the largest image
        picture_element = profile['profilePicture']['displayImage~']['elements'][-1]
        picture_url = picture_element['identifiers'][0]['identifier']
        try:
            r = requests.get(picture_url)
            new_file = frappe.get_doc({
                'doctype': 'File',
                'file_name': '{}_profile.jpg'.format(payload['email']),
                'content': r.content,
                'decode': False
            })
            new_file.save()
            frappe.db.commit()
            payload['picture'] = new_file.file_url
        except Exception as e:
            print(str(e))
            payload['picture'] = picture_url
    return payload

@frappe.whitelist(allow_guest=True)
def send_sms_2_recipients(recipients, message):
    from frappe.core.doctype.sms_settings.sms_settings import send_sms
    # hostname = 'https://openinnovationplatform.org'
    # Strip out + when sending SMS
    send_sms(recipients, message)


@frappe.whitelist(allow_guest=True)
def deploy_apps():
    from frappe.utils.background_jobs import enqueue
    try:
        enqueue(update_apps_via_git, timeout=1200)
        return True
    except Exception as e:
        print(str(e))
        raise

@frappe.whitelist(allow_guest=True)
def update_apps_via_git():
    import shlex, subprocess, os
    os.chdir('/home/cr/frappe-bench/apps/contentready_oip')
    cmds = ['git pull', 'bench --site openinnovationplatform.org migrate', 'find . -iname *.pyc -delete', 'bench restart']
    try:
        for cmd in cmds:
            cmd = shlex.split(cmd)
            subprocess.check_output(cmd)
        return True
    except Exception as e:
        print(str(e))
        raise

@frappe.whitelist(allow_guest=True)
def share_doctype(recipients,doctype,docname,mode='email'):
    try:
        if isinstance(recipients,str):
            recipients = json.loads(recipients)
        if frappe.session.user != 'Guest':
            user = frappe.get_doc('User Profile', frappe.session.user).as_dict()
        else:
            user = {'first_name': 'An OIP contributor'}
        context = {}
        context.update(user)
        context['doctype'] = doctype.lower()
        hostname = get_url()
        if not hostname:
            hostname = 'https://openinnovationplatform.org'
        context['url'] = hostname + '/' + frappe.get_value(doctype, docname, 'route')
        r = get_email_template('Share Content', context)
        subject = r['subject'].replace('doctype', doctype.lower())
        frappe.sendmail(recipients, subject=subject, message=r['message'], delayed=True)
        return True
    except Exception as e:
        print(str(e))
        return False

def send_weekly_updates(emails=[]):
    from datetime import datetime, timedelta
    if emails:
        profiles = frappe.get_all('User Profile', filters={'user': ['in', emails]})
    else:
        profiles = frappe.get_all('User Profile')
    hostname = get_url()
    if not hostname:
        hostname = 'https://openinnovationplatform.org'
    response = {}
    for p in profiles:
        try:
            user = frappe.get_doc('User Profile', p['name'])
            sectors = [sector.sector for sector in user.sectors]
            today = datetime.now()
            start = today - timedelta((today.weekday()) % 7)
            midnight = datetime.combine(start, datetime.min.time())
            context = {}
            context['problems'] = get_content_recommended_for_user('Problem', sectors, limit_page_length=5,creation=midnight)
            context['solutions'] = get_content_recommended_for_user('Solution', sectors, limit_page_length=5,creation=midnight)
            template = 'templates/includes/common/homepage_showcase_content.html'
            context['content_html'] = frappe.render_template(template, context)
            context['unsubscribe_link'] = '<a href="{}/api/method/contentready_oip.api.unsubscribe_email?email={}">Click here</a>'.format(hostname,user.user)
            r = get_email_template('Weekly Updates', context)
            print(r)
            frappe.sendmail(user.user, subject=r['subject'], message=r['message'], delayed=True)
            response[user.user] = r
        except Exception as e:
            print(str(e))
            response[p['name']] = str(e)
    return response 

@frappe.whitelist(allow_guest=False)
def add_custom_domain(domain):
    import shlex, subprocess
    site = frappe.get_site_path()
    cmds = ['bench setup add-domain {} --site {}'.format(domain, site), 'sudo -H bench setup lets-encrypt -n {} --custom-domain {}'.format(site, domain), 'sudo systemctl restart nginx']
    try:
        for cmd in cmds:
            cmd = shlex.split(cmd)
            subprocess.check_output(cmd)
        doc = frappe.get_doc('OIP White Label Domain', domain)
        doc.url = 'https://{}'.format(domain)
        doc.save()
        return True
    except Exception as e:
        print(str(e))
        raise

def setup_domain_hook(doc=None, event_name=None):
    try:
        add_custom_domain(doc.domain)
    except Exception as e:
        print(str(e))

@frappe.whitelist(allow_guest=False)
def set_document_value(doctype, docname, fieldname, fieldvalue):
    return frappe.set_value(doctype, docname, fieldname, fieldvalue)

@frappe.whitelist(allow_guest=False)
def get_searched_content(index_name,search_str,filters=None):
    options = {
        "attributesToHighlight" : ["*"]
    }
    if filters:
        options["filters"] = filters
    
    index = CLIENT.get_index(index_name.lower())
    result = index.search(search_str,options)
    
    if index_name == 'user_profile':
        return result['hits']
    else:
        apply_range_filter = filter_content_by_range(result['hits'], index_name)
        return apply_range_filter

@frappe.whitelist(allow_guest=False)
def get_searched_content_es(index_name,search_str,filters=None):
    client = Elasticsearch('https://search-contentready-es-knpak5szkr5ljrj2kvgfu36qz4.ap-south-1.es.amazonaws.com')
    index_name = index_name.replace(' ', '_').lower()
    search_str = '*{}*'.format(search_str)
    q = Q("wildcard", doc__title=search_str) | Q("wildcard", doc__description=search_str)
    s = Search(using=client, index=index_name).query(q)
    response = s.execute()
    results = []
    for r in response:
        try:
            doctype = r.doc.doctype
            docname = r.doc.name
            doc = refactor_2_list_str(frappe.get_doc(doctype, docname).as_dict(), 'sectors','sector')
            results.append(doc)
        except:
            pass
    if index_name == 'user_profile':
        return results
    else:
        return filter_content_by_range(results, doctype)
         

def filter_content_by_range(searched_content,doctype):
    content = []
    try:
        parameters = frappe.form_dict
        # filter_location_name
        try:
            filter_location_name = parameters['loc']
        except:
            filter_location_name = None
        # filter_location_lat
        try:
            filter_location_lat = float(parameters['lat'])
        except:
            filter_location_lat = None
        # filter_location_lng
        try:
            filter_location_lng = float(parameters['lng'])
        except:
            filter_location_lng = None
        # filter_location_range
        try:
            filter_location_range = int(parameters['rng'])
        except:
            filter_location_range = None
        try:
            user = frappe.get_doc('User Profile', frappe.session.user)
            user_sectors = {sector.sector for sector in user.sectors}
        except:
            user_sectors = set()

        from geopy import distance
        for doc in searched_content:    
            try:
                if doc["is_published"]:
                    if (doc["latitude"] != None) and (doc["longitude"] != None) and (filter_location_lat != None) and (filter_location_lng != None) and (filter_location_range != None):
                        distance_km = distance.distance((filter_location_lat, filter_location_lng), (float(doc["latitude"]), float(doc["longitude"]))).km
                        if distance_km > filter_location_range:
                            # skip this document as it's outside our bounds
                            continue
                    
                    if user_sectors:
                        doc_sectors = {sector["sector"] for sector in doc["sectors"]}
                        relevant_sectors = doc_sectors.intersection(user_sectors)
                        if doctype == 'Problem':
                            doc["score"] = 0.3 * len(doc["validations"]) + 0.1 * len(doc["likes"]) + 0.1 * len(doc["enrichments"]) + 0.1 * len(doc["watchers"]) + 0.05 * len(doc["discussions"]) + 0.3 * len(relevant_sectors)
                        else:
                            doc["score"] = 0.3 * len(doc["validations"]) + 0.1 * len(doc["likes"]) + 0.1 * len(doc["watchers"]) + 0.05 * len(doc["discussions"]) + 0.3 * len(relevant_sectors)
                    else:
                        doc["score"] = 1
                    content.append(doc)
            except Exception as e:
                print(str(e))    
    except Exception as e:
        print(str(e))
    content.sort(key=lambda x: x["score"], reverse=True)
    return content

def replace_space(name):
    """
    replace white space with _
    """
    name_list = name.split(" ")
    if len(name_list) > 1:
        name = "_".join(name_list)

    return name.lower()

def refactor_2_list_str(doc_dict, p_key, c_key):
    """
    Refactor sector or persona to list of strings.

    Parameters: 
    doc_dict (dict): Dictionary of doctype. \n
    p_key (str): primary key of doctype.\n
    c_key (str): child key of primary key's value.

    Returns: 
    doc_dict (dict): Updated dictionary of doctype.
    """
    try:
        refactor_list = doc_dict[p_key]
        new_key = "meili_{}".format(p_key)
        doc_dict[new_key] = []

        for item in refactor_list:
            doc_dict[new_key].append(item[c_key])
    except Exception as _e:
        print(str(_e))

    return doc_dict

def update_doc_to_meilisearch(doc, hook_action):
    try:
        if doc.is_published:
            index_name = replace_space(doc.doctype)
            j = doc.as_json()
            document = refactor_2_list_str(json.loads(j), 'sectors','sector')
            index = CLIENT.get_index(index_name)
            index.add_documents([document])
    except Exception as _e:
        print(str(_e))

def update_user_profile_to_meilisearch(doc, hook_action):
    try:
        document = doc.as_dict()
        index_name = replace_space(document['doctype'])
        # https://docs.python.org/3/library/stdtypes.html#str.isalnum
        document['meili_idx'] = "".join(v for v in document['name'] if v.isalnum())
        document = refactor_2_list_str(document, 'sectors','sector')
        document = refactor_2_list_str(document, 'personas', 'persona')
        index = CLIENT.get_index(index_name)
        index.add_documents([document])
    except Exception as _e:
        print(str(_e))


def add_doc_to_elasticsearch(doc, hook_action='on_update'):
    try:
        connections.create_connection(hosts=['https://search-contentready-es-knpak5szkr5ljrj2kvgfu36qz4.ap-south-1.es.amazonaws.com'])
        doctype = doc.doctype.replace(' ', '_').lower()
        class Content(Document):
            doc = Object()
            class Index:
                name = doctype
        Content.init()
        if doc.is_published:
            content = Content(meta={'id': doc.name})
            content.doc = refactor_2_list_str(doc.as_dict(), 'sectors','sector')
            if doctype == 'User Profile':
                content.doc = refactor_2_list_str(content.doc, 'personas','persona')
            content.save()
    except Exception as _e:
        print(str(_e))

@frappe.whitelist(allow_guest=True)
def has_admin_role():
    roles = frappe.get_roles(frappe.session.user);
    allowed_roles = ["Administrator", "System Manager"]
    is_allowed = False
    for role in allowed_roles:
        if role in roles:
            is_allowed = True
    
    return is_allowed


@frappe.whitelist(allow_guest=True)
def get_url_metadata(url):
    import requests
    import re

    rejex = "((http(s)?:\/\/)?)(www\.)?((youtube\.com\/)|(youtu.be\/))[\S]+"
    pattern = re.compile(rejex)
    
    if(pattern.match(url)):
        youtubeApi = "https://www.youtube.com/oembed?url={}&format=json".format(url)
        r = requests.get(youtubeApi)
        response = {}
        response["provider"] = "youtube"
        response["data"] = r.json()
        return response
    else: 
        vimeoId = url.split("https://vimeo.com/")[1]
        vimeoApi = "https://vimeo.com/api/v2/video/{}.json".format(vimeoId)
        r = requests.get(vimeoApi)
        response = {}
        response["provider"] = "vimeo"
        response["data"] = r.json()[0]
        return response
    
@frappe.whitelist(allow_guest=False)
def get_beneficiaries_from_sectors(sectors):
    beneficiary_list = set()
    try:
        sectors = json.loads(sectors)
        for sector in sectors:
            s = frappe.get_doc('Sector', sector)
            for b in s.beneficiaries:
                beneficiary_list.add(b.beneficiary)

        return beneficiary_list
    except Exception as e:
        print(str(e))