# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "contentready_oip"
app_title = "ContentReady OIP"
app_publisher = "ContentReady"
app_description = "Open Innovation Platform"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "hello@contentready.co"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/contentready_oip/css/contentready_oip.css"
# app_include_js = "/assets/contentready_oip/js/contentready_oip.js"

# include js, css files in header of web template
# web_include_css = "/assets/contentready_oip/css/contentready_oip.css"
# web_include_js = "/assets/contentready_oip/js/contentready_oip.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "contentready_oip.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
website_generators = ["Web Page", "Problem"]

# Installation
# ------------

# before_install = "contentready_oip.install.before_install"
# after_install = "contentready_oip.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "contentready_oip.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"contentready_oip.tasks.all"
# 	],
# 	"daily": [
# 		"contentready_oip.tasks.daily"
# 	],
# 	"hourly": [
# 		"contentready_oip.tasks.hourly"
# 	],
# 	"weekly": [
# 		"contentready_oip.tasks.weekly"
# 	]
# 	"monthly": [
# 		"contentready_oip.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "contentready_oip.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "contentready_oip.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "contentready_oip.task.get_dashboard_data"
# }

