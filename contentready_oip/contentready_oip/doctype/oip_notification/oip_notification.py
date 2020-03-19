# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class OIPNotification(Document):
	def autoname(self):
		try:
			self.name = '{}-{}-{}'.format(self.target_user, self.source_user, self.child_name)
		except:
			pass
