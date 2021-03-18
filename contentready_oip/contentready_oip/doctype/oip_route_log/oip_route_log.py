# -*- coding: utf-8 -*-
# Copyright (c) 2021, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class OIPRouteLog(Document):
	pass
	# def before_save(self):
	# 	if self.route.startswith('problems'):
	# 		self.parent_doctype = 'Problem'
	# 		self.parent_name = frappe.db.get_list(self.parent_doctype, filters={'route': self.route})[0]['name']
