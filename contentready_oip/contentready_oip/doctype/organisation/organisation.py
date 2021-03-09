# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.website.website_generator import WebsiteGenerator

class Organisation(WebsiteGenerator):
    def make_route(self):
        # This method overrides the parent class method to use a route prefix
        # that is independent of the doctype setting.
        '''Returns the default route. If `route` is specified in DocType it will be
        route/title'''
        from_title = self.scrubbed_title()
        return 'organisations' + '/' + from_title
