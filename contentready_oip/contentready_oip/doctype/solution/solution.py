# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.utils.html_utils import clean_html

class Solution(WebsiteGenerator):
    def make_route(self):
        # This method overrides the parent class method to use a route prefix
        # that is independent of the doctype setting.
        '''Returns the default route. If `route` is specified in DocType it will be
        route/title'''
        from_title = self.scrubbed_title()
        route = 'solutions/' + from_title
        similar_content = frappe.get_all('Solution', filters={'route': route})
        if len(similar_content) > 0:
            from_title = self.scrubbed_title()+'-'+frappe.generate_hash("", 3)
        return 'solutions/' + from_title

    def autoname(self):
        # Override autoname from parent class to allow creation of problems with the same name.
        # We add a randomised suffix to distinguish problems with the same name.
        if frappe.db.exists('Solution', self.scrubbed_title()):
            self.name = self.scrubbed_title()+'-'+frappe.generate_hash("", 3)

    def before_save(self):
        try:
            self.short_description = clean_html(self.description)[:500]
            if len(self.description) > 1000:
                self.short_description += '...'
        except:
            pass
        try:
            self.org_title = frappe.get_value(
                'Organisation', self.org, 'title')
        except:
            pass

    def on_update(self):
        if self.is_published:
            # Add reference to this solution in each of the problems_addressed
            # for p in self.problems_addressed:
            #     problem = frappe.get_doc('Problem', p.problem)
            #     problem.add_solution(self)
            #     frappe.db.commit()
            # read all child tables and add notifications
            self.create_notifications()
        # use sets for sectors
        sectors = {s.sector for s in self.sectors}
        self.sectors = []
        for sector in sectors:
            r = self.append('sectors', {})
            r.sector = sector
    
    def create_notifications(self):
        # notify owner when someone enriches
        template = {
            'doctype': 'OIP Notification',
            'target_user': self.owner,
            'parent_doctype': self.doctype,
            'parent_name': self.name,
        }
        verbs = {
            'Validation': 'validated',
            'Collaboration': 'wants to collaborate on',
            'Discussion': 'added a comment on',
            'Like': 'liked',
        }
        doctypes = ['Validation', 'Collaboration', 'Discussion', 'Like']
        for doctype in doctypes:
            try:
                contrib_list = frappe.get_list(doctype, fields=['name', 'owner'], filters={'parent_doctype': self.doctype, 'parent_name': self.name})
                for c in contrib_list:
                    # do not create notifications if the owner themselves contributed
                    if c['owner'] == self.owner:
                        continue
                    n_template = template.copy()
                    n_template['child_name'] = c['name']
                    n_template['child_doctype'] = doctype
                    n_template['source_user'] = c['owner']
                    n_name = '{}-{}-{}'.format(n_template['target_user'], n_template['source_user'], n_template['child_name'])
                    if frappe.db.exists('OIP Notification', n_name):
                        continue
                    user = frappe.get_doc('User', c['owner'])
                    n_template['text'] = '{} {} your {}: {}'.format(user.full_name, verbs[doctype], self.doctype.lower(), self.title)
                    n_template['route'] = self.route + '#' + doctype.lower() + 's'
                    notification = frappe.get_doc(n_template)
                    notification.save()
            except:
                pass
        frappe.db.commit()

    def get_context(self, context):
        # print("solution.py, get_context", context.keys())
        # context.ping = 'pong'
        return context