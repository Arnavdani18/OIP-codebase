from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Users"),
			"items": [
				{
					"type": "doctype",
					"name": "User Profile",
				},
				{
					"type": "doctype",
					"name": "Organisation"
				},
				{
					"type": "doctype",
					"name": "Persona"
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
				{
					"type": "doctype",
					"name": "OIP Project",
					"label": "Project",
				}
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
					"name": "Skill",
				},
				{
					"type": "doctype",
					"name": "Qualification",
				}
			]
		},
	]
