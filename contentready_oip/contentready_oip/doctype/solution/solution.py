# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.utils.html_utils import clean_html
from contentready_oip import api

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
		# Override autoname from parent class to allow creation of solutions with the same name.
		# We add a randomised suffix to distinguish solutions with the same name.
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
		sectors = {s.sector for s in self.sectors}
		self.sectors = []
		for sector in sectors:
			r = self.append('sectors', {})
			r.sector = sector
		self.maybe_assign_image()
		old = self.get_doc_before_save()
		if old and not old.is_published and self.is_published:
			self.maybe_create_insert_notifications()

	def maybe_assign_image(self):
		if len(self.media) == 0:
			if len(self.sectors) > 0:
				for s in self.sectors:
					sector_image = frappe.db.get_value('Sector', s.sector, 'image')
					if sector_image:
						break
				if sector_image:
					row = self.append('media', {})
					row.attachment = sector_image
					row.is_featured = True
					row.type = 'image/jpeg'

	def maybe_create_insert_notifications(self):
		try:
			source_full_name = frappe.db.get_value('User Profile', self.owner, 'full_name')
			parent_doctype = 'Problem'
			for problem in self.problems_addressed:
				parent_name = problem.problem
				content_title, content_route = frappe.db.get_value(parent_doctype, parent_name, ['title', 'route'])
				recipient = frappe.db.get_value(parent_doctype, parent_name, 'owner')
				notification = frappe.get_doc({
					'doctype': 'OIP Notification',
					'source_user': self.owner,
					'target_user': recipient,
					'parent_doctype': parent_doctype,
					'parent_name': parent_name,
					'child_doctype': self.doctype,
					'child_name': self.name,
					'text': '{} added a solution to your {}: {}'.format(source_full_name, parent_doctype.lower(), content_title),
					'route': content_route + '#' + self.doctype.lower() + 's',
				})
				notification.save()
		except:
			pass

	def get_context(self, context):
		context.is_collaborator = api.has_collaborator_role()
		context.is_service_provider = api.has_service_provider_role()
		context.collaborations = frappe.get_list('Collaboration', filters={'parent_doctype': self.doctype, 'parent_name': self.name})
		context.validations = frappe.get_list('Validation', filters={'parent_doctype': self.doctype, 'parent_name': self.name})
		context.likes = frappe.get_list('Like', filters={'parent_doctype': self.doctype, 'parent_name': self.name})
		context.watchers = frappe.get_list('Watch', filters={'parent_doctype': self.doctype, 'parent_name': self.name})
		# Log visit
		if frappe.session.user != self.owner:
			api.enqueue_log_route_visit(route=context.route, user_agent=frappe.request.headers.get('User-Agent'), parent_doctype=self.doctype, parent_name=self.name)
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