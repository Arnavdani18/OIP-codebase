# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.utils.html_utils import clean_html


class Problem(WebsiteGenerator):
    def make_route(self):
        # This method overrides the parent class method to use a route prefix
        # that is independent of the doctype setting.
        '''Returns the default route. If `route` is specified in DocType it will be
        route/title'''
        from_title = self.scrubbed_title()
        route = 'problems/' + from_title
        similar_content = frappe.get_all('Problem', filters={'route': route})
        if len(similar_content) > 0:
            from_title = self.scrubbed_title()+'-'+frappe.generate_hash("", 3)
        return 'problems/' + from_title

    def autoname(self):
        # Override autoname from parent class to allow creation of problems with the same name.
        # We add a randomised suffix to distinguish problems with the same name.
        if frappe.db.exists('Problem', self.scrubbed_title()):
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
        # use sets for sectors
        sectors = {s.sector for s in self.sectors}
        self.sectors = []
        for sector in sectors:
            r = self.append('sectors', {})
            r.sector = sector

    def add_solution(self, new_solution=None):
        solution_set = set()
        for s in self.solutions:
            solution_set.add(s.solution)
        if new_solution:
            solution_set.add(new_solution.name)
        self.solutions = []
        for s in solution_set:
            r = self.append('solutions', {})
            r.solution = s
        # if new_solution:
        #     r = self.append('solutions', {})
        #     r.solution = new_solution.name
        self.save()

    def on_update(self):
        # read all child tables and add notifications
        self.create_notifications()
    
    def create_notifications(self):
        # notify owner when someone enriches
        template = {
            'doctype': 'OIP Notification',
            'target_user': self.owner,
            'parent_doctype': self.doctype,
            'parent_name': self.name,
        }
        verbs = {
            'Enrichment Table': 'enriched',
            'Validation Table': 'validated',
            'Collaboration Table': 'wants to collaborate on',
            'Discussion Table': 'added a comment on',
            'Like Table': 'liked',
            'Solution Table': 'added a solution to',
        }
        for c in self.enrichments + self.validations + self.collaborations + self.discussions + self.likes:
            try:
                # do not create notifications if the owner themselves contributed
                if c.user == self.owner:
                    continue
                n_template = template.copy()
                n_template['parent_field'] = c.parentfield
                n_template['child_name'] = c.name
                n_template['child_doctype'] = c.doctype
                n_template['source_user'] = c.user
                n_name = '{}-{}-{}'.format(n_template['target_user'], n_template['source_user'], n_template['child_name'])
                # This prevents duplicates
                if frappe.db.exists('OIP Notification', n_name):
                    continue
                user = frappe.get_doc('User', c.user)
                n_template['text'] = '{} {} your {}: {}'.format(user.full_name, verbs[c.doctype], self.doctype.lower(), self.title)
                n_template['route'] = self.route + '#' + c.parentfield
                notification = frappe.get_doc(n_template)
                notification.save()
            except:
                pass
        for c in self.solutions:
            try:
                doc = frappe.get_doc('Solution', c.solution)
                # do not create notifications if the owner themselves contributed
                if doc.owner == self.owner:
                    continue
                n_template = template.copy()
                n_template['parent_field'] = c.parentfield
                n_template['child_name'] = c.name
                n_template['child_doctype'] = c.doctype
                n_template['source_user'] = doc.owner
                n_name = '{}-{}-{}'.format(n_template['target_user'], n_template['source_user'], n_template['child_name'])
                if frappe.db.exists('OIP Notification', n_name):
                    continue
                user = frappe.get_doc('User', doc.owner)
                n_template['text'] = '{} {} your {}: {}'.format(user.full_name, verbs[c.doctype], self.doctype.lower(), self.title)
                n_template['route'] = doc.route
                notification = frappe.get_doc(n_template)
                notification.save()
            except:
                pass
        frappe.db.commit()

    def get_context(self, context):
        # published_enrichments = [e for e in self.enrichments if e.is_published]
        context.enrichment_count = frappe.db.count("Enrichment", {'Problem': context.name ,'is_published': True})
        return context
