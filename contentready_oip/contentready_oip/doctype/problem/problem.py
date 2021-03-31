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
		solution_ids = frappe.get_list('Problem Table', filters={'problem': self.name, 'parenttype': 'Solution'}, fields=['parent'])
		solution_ids = [s['parent'] for s in solution_ids]
		context.solutions = frappe.get_list('Solution', filters={'name': ['in', solution_ids], 'is_published': True})
		context.enrichments = frappe.get_list('Enrichment', filters={'parent_doctype': self.doctype, 'parent_name': self.name, 'is_published': True})
		context.collaborations = frappe.get_list('Collaboration', filters={'parent_doctype': self.doctype, 'parent_name': self.name})
		context.validations = frappe.get_list('Validation', filters={'parent_doctype': self.doctype, 'parent_name': self.name})
		context.likes = frappe.get_list('Like', filters={'parent_doctype': self.doctype, 'parent_name': self.name})
		context.watchers = frappe.get_list('Watch', filters={'parent_doctype': self.doctype, 'parent_name': self.name})
		context.enrichment_count = len(context.enrichments)
		# Log visit
		api.enqueue_log_route_visit(route=context.route, user_agent=frappe.request.headers.get('User-Agent'), parent_doctype=self.doctype, parent_name=self.name)
		context.is_collaborator = api.has_collaborator_role()
		context.is_service_provider = api.has_service_provider_role()
		try:
			context.analytics = frappe.get_doc('OIP Route Aggregate', {'route': self.route})
		except:
			context.analytics = {
				'total_visits': 0,
				'unique_visitors': 0,
				'unique_organisations': 0,
				'modified': None
			}
		return context
