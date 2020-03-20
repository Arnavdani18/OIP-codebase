# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator


class UserProfile(WebsiteGenerator):
    def make_route(self):
        # This method overrides the parent class method to use a route prefix
        # that is independent of the doctype setting.
        '''Returns the default route. If `route` is specified in DocType it will be
        route/title'''
        from_title = self.scrubbed_title()
        return 'contributors' + '/' + from_title

    def autoname(self):
        # Override autoname from parent class to allow creation of problems with the same name.
        # We add a randomised suffix to distinguish problems with the same name.
        if frappe.db.exists('User Profile', self.scrubbed_title()):
            self.name = self.scrubbed_title()+'-'+frappe.generate_hash("", 3)

    def on_update(self):
        if self.org_title:
            try:
                org = frappe.get_doc('Organisation', {'title': self.org_title})
            except:
                org = frappe.get_doc({
                    'doctype': 'Organisation',
                    'title': self.org_title
                })
                org.insert()
            self.org = org.name
        # use sets for sectors and personas
        sectors = {s.sector for s in self.sectors}
        self.sectors = []
        for sector in sectors:
            r = self.append('sectors', {})
            r.sector = sector
        personas = {s.persona for s in self.personas}
        self.personas = []
        for persona in personas:
            r = self.append('personas', {})
            r.persona = persona
        frappe.db.commit()
