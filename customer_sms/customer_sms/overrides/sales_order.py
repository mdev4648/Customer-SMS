# import frappe
# from frappe import _


# def validate_sales_order(doc, method):
#     pass
#     allowed = frappe.db.get_all(
#         "User Permission",
#         filters={"user": frappe.session.user, "allow": "Branch"},
#         pluck="for_value",
#     )

#     if not doc.branch:
#         frappe.throw(_("Branch is required."))

#     if frappe.session.user != "Administrator" and doc.custom_branch not in allowed:
#         frappe.throw(
#             _("You are not allowed to create Sales Orders for branch {0}").format(
#                 doc.custom_branch
#             )
#         )


import frappe
from frappe import _


def validate_sales_order(doc, method):
    # 1. Get the employee linked with this user
    employee = frappe.db.get_value(
        "Employee", {"user_id": frappe.session.user}, ["name", "branch"], as_dict=True
    )

    if not employee:
        frappe.throw(
            _("No Employee record found for user {0}. Please contact HR/Admin.").format(
                frappe.session.user
            )
        )

    if not employee.branch:
        frappe.throw(
            _(
                "Employee {0} does not have a Branch assigned. Please contact Admin."
            ).format(employee.name)
        )

    # 2. Get allowed branches from User Permission
    allowed_branches = frappe.db.get_all(
        "User Permission",
        filters={"user": frappe.session.user, "allow": "Branch"},
        pluck="for_value",
    )

    if not allowed_branches:
        frappe.throw(
            _("You don’t have permission for any Branch. Please contact Admin.")
        )

    # 3. Check if Employee branch is in User Permission list
    if employee.branch not in allowed_branches:
        frappe.throw(
            _(
                "Your branch {0} is not in your allowed branch list. Please contact Admin."
            ).format(employee.branch)
        )

    # 4. Ensure user has only one allowed branch
    if len(allowed_branches) > 1:
        frappe.throw(
            _(
                "You have access to multiple branches. Please contact Admin to restrict you to one branch."
            )
        )

    # 5. Set branch on Sales Order (readonly field)
    doc.custom_branch = employee.branch
