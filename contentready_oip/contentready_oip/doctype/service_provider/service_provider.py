# -*- coding: utf-8 -*-
# Copyright (c) 2021, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator

class ServiceProvider(WebsiteGenerator):
	def make_route(self):
        # This method overrides the parent class method to use a route prefix
        # that is independent of the doctype setting.
        '''Returns the default route. If `route` is specified in DocType it will be
        route/title'''
        from_title = self.scrubbed_title()
        return 'service-providers' + '/' + from_title
    
    def before_save(self):
        # print("before_save", self.as_dict())
        pass

    def autoname(self):
        # Override autoname from parent class to allow creation of service providers with the same name.
        # We add a randomised suffix to distinguish service providers with the same name.
        if frappe.db.exists('Service Provider', self.scrubbed_title()):
            self.name = self.scrubbed_title()+'-'+frappe.generate_hash("", 3)
