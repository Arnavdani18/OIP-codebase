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
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Organisation"
				},
			]
		},
		{
			"label": _("Collaboration"),
			"items": [
				{
					"type": "doctype",
					"name": "Problem",
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Solution",
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "OIP Project",
					"label": "Project",
					"onboard": 1,
				}
			]
		},
		{
			"label": _("Configuration"),
			"items": [
				{
					"type": "doctype",
					"name": "Skill",
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Qualification",
					"onboard": 1,
				}
			]
		},
	]
