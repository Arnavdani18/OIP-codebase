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
			self.name = self.scrubbed_title()+'-'+frappe.generate_hash("",3)

	def before_insert(self):
		try:
			org = frappe.get_doc('Organisation', {'org_title': self.org_title})
		except:
			org = frappe.get_doc({
				'doctype': 'Organisation',
				'title': self.org_title
			})
			org.insert()
		self.org = org.name
	
	def on_update(self):
		# print(self.photo)
		if self.photo:
			frappe.set_value('User', self.user, 'user_image', self.photo)
			frappe.db.commit()
