# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from contentready_oip import api

class Organisation(WebsiteGenerator):
	def make_route(self):
		# This method overrides the parent class method to use a route prefix
		# that is independent of the doctype setting.
		'''Returns the default route. If `route` is specified in DocType it will be
		route/title'''
		from_title = self.scrubbed_title()
		return 'organisations' + '/' + from_title
	
	def autoname(self):
		# Override autoname from parent class to allow creation of organisations with the same name.
		# We add a randomised suffix to distinguish organisations with the same name.
		if frappe.db.exists('Organisation', self.scrubbed_title()):
			self.name = self.scrubbed_title()+'-'+frappe.generate_hash("", 3)
	
	def get_context(self, context):
		# Log visit
		if frappe.session.user != self.owner:
			api.enqueue_log_route_visit(route=context.route, user_agent=frappe.request.headers.get('User-Agent'), parent_doctype=self.doctype, parent_name=self.name)
		return context
	
	def approve(self):
		if not api.has_admin_role():
			frappe.throw('This method can only be run by a system manager')
		ok = api.invite_user(self.email, first_name=self.first_name, last_name=self.last_name, roles=['Service Provider'])
		if ok:
			self.user = self.email
			self.is_published = True
			self.owner = self.user
			self.save()
			user_profile = frappe.get_doc('User Profile', self.user)
			user_profile.append('personas',{'persona': 'service_provider'})
			user_profile.save()
		return ok