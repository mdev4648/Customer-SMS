app_name = "customer_sms"
app_title = "Customer Sms"
app_publisher = "md"
app_description = "sms integration"
app_email = "md@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "customer_sms",
# 		"logo": "/assets/customer_sms/logo.png",
# 		"title": "Customer Sms",
# 		"route": "/customer_sms",
# 		"has_permission": "customer_sms.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/customer_sms/css/customer_sms.css"
app_include_js = "/assets/customer_sms/js/sms.js"

# include js, css files in header of web template
# web_include_css = "/assets/customer_sms/css/customer_sms.css"
# web_include_js = "/assets/customer_sms/js/customer_sms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "customer_sms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Client SMS Log": "customer_sms/client_scripts/client_sms_log.js"}
doctype_list_js = {
    "Client SMS Log": "customer_sms/client_scripts/client_sms_log_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "customer_sms/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "customer_sms.utils.jinja_methods",
# 	"filters": "customer_sms.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "customer_sms.install.before_install"
# after_install = "customer_sms.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "customer_sms.uninstall.before_uninstall"
# after_uninstall = "customer_sms.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "customer_sms.utils.before_app_install"
# after_app_install = "customer_sms.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "customer_sms.utils.before_app_uninstall"
# after_app_uninstall = "customer_sms.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "customer_sms.notifications.get_notification_config"

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

doc_events = {
    "sms": {"on_submit": "customer_sms.api.send_sms_on_submit"},
    "Sales Order": {
        "validate": "customer_sms.customer_sms.overrides.sales_order.validate_sales_order"
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# "all": ["customer_sms.jobs.sync_sms_log.sync_sms_logs"],
# "daily": [
# 	"customer_sms.tasks.daily"
# ],
# "hourly": [
# 	"customer_sms.tasks.hourly"
# ],
# "weekly": [
# 	"customer_sms.tasks.weekly"
# ],
# "monthly": [
# 	"customer_sms.tasks.monthly"
# ],
# }

# Testing
# -------

# before_tests = "customer_sms.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "customer_sms.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "customer_sms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "customer_sms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["customer_sms.utils.before_request"]
# after_request = ["customer_sms.utils.after_request"]

# Job Events
# ----------
# before_job = ["customer_sms.utils.before_job"]
# after_job = ["customer_sms.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"customer_sms.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
