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
		return 'solutions' + '/' + from_title
	
	def autoname(self):
		# Override autoname from parent class to allow creation of problems with the same name.
		# We add a randomised suffix to distinguish problems with the same name.
		if frappe.db.exists('Solution', self.scrubbed_title()):
			self.name = self.scrubbed_title()+'-'+frappe.generate_hash("",3)

	def before_save(self):
		try:
			self.short_description = clean_html(self.description)[:500]
			if len(self.description) > 1000:
				self.short_description += '...'
		except:
			pass
		try:
			self.org_title = frappe.get_value('Organisation', self.org, 'title')
		except:
			pass

	def after_save(self):
		# Add reference to this solution in each of the problems_addressed
		for p in self.problems_addressed:
			problem = frappe.get_doc('Problem', p.problem)
			s = problem.append('solutions', {})
			s.solution = self.name
			problem.save()
			frappe.db.commit()

