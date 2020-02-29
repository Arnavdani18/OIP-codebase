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
		return 'problems' + '/' + from_title
	
	def autoname(self):
		# Override autoname from parent class to allow creation of problems with the same name.
		# We add a randomised suffix to distinguish problems with the same name.
		if frappe.db.exists('Problem', self.scrubbed_title()):
			self.name = self.scrubbed_title()+'-'+frappe.generate_hash("",3)

	# def get_context(self, context):
	# 	print(self.as_dict())
		# context.enrichments = self.enrichments
		# context.discussions = self.discussions
		# print(context)

	def before_save(self):
		self.short_description = clean_html(self.description)[:500]
		if len(self.description) > 1000:
			self.short_description += '...'