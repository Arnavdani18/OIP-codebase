from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Users"),
			"items": [
				{
					"label": "User List",
					"type": "doctype",
					"name": "User",
				},
				{
					"type": "doctype",
					"name": "User Profile",
				},
				{
					"type": "doctype",
					"name": "Organisation"
				},
			]
		},
		{
			"label": _("Content"),
			"items": [
				{
					"type": "doctype",
					"name": "Problem",
				},
				{
					"type": "doctype",
					"name": "Enrichment",
				},
				{
					"type": "doctype",
					"name": "Solution",
				},
				{
					"type": "doctype",
					"name": "Discussion",
				},
				# {
				# 	"type": "doctype",
				# 	"name": "OIP Project",
				# 	"label": "Project",
				# }
			]
		},
		{
			"label": _("Configuration"),
			"items": [
				{
					"type": "doctype",
					"name": "Sector"
				},
				{
					"type": "doctype",
					"name": "Persona"
				},
				# {
				# 	"type": "doctype",
				# 	"name": "Skill",
				# },
				# {
				# 	"type": "doctype",
				# 	"name": "Qualification",
				# },
				{
					"label": "White Label Domains",
					"type": "doctype",
					"name": "OIP White Label Domain",
				}
			]
		},
	]
