# -*- coding: utf-8 -*-
# Copyright (c) 2019, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator

class Problem(WebsiteGenerator):
    # website = frappe._dict(
    #     template = "templates/problems_grid.html",
    #     condition_field = "published",
    #     page_title_field = "title",
    # )

    def get_context(self, context):
        pass
        # show breadcrumbs
        # context.parents = [{'name': 'jobs', 'title': _('All Jobs') }]
    
    def get_list_context(self, context):
        context.title = _("Problems")
        context.introduction = _('Current Problems')
