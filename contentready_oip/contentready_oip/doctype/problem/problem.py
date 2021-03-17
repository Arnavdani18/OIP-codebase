# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.utils.html_utils import clean_html
from contentready_oip import api

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

    def get_context(self, context):
        context.enrichment_count = frappe.db.count("Enrichment", {'parent_name': context.name ,'is_published': True})
        solution_ids = frappe.get_list('Problem Table', filters={'problem': self.name, 'parenttype': 'Solution'}, fields=['parent'])
        solution_ids = [s['parent'] for s in solution_ids]
        context.solutions = frappe.get_list('Solution', filters={'name': ['in', solution_ids], 'is_published': True})
        # Log visit
        api.enqueue_log_route_visit(route=context.route, user_agent=frappe.request.headers.get('User-Agent'))
        return context
