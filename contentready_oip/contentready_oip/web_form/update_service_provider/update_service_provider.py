from __future__ import unicode_literals

import frappe

def get_context(context):
	try:
		context.title = context.doc.full_name
	except:
		context.title = 'Update Service Provider Profile'
	return context
