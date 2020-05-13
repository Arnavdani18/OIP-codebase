# -*- coding: utf-8 -*-
# Copyright (c) 2020, ContentReady and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class CollaborationIntent(Document):
	def on_update(self):
		personas_list = [p.persona for p in self.personas]
		self.personas_list = ','.join(personas_list)
