// frappe.listview_settings["Client SMS Log"] = {
// 	onload: function (listview) {
// 		listview.page.add_action_item(__("Resend Failed SMS"), function () {
// 			let selected = listview.get_checked_items();

// 			if (!selected.length) {
// 				frappe.msgprint("Please select at least one Failed SMS log.");
// 				return;
// 			}

// 			frappe.call({
// 				method: "customer_sms.api.bulk_resend_sms",
// 				args: {
// 					logs: selected.map((d) => d.name),
// 				},
// 				callback: function (r) {
// 					if (!r.exc) {
// 						frappe.msgprint(__("Selected Failed SMS have been re-queued."));
// 						listview.refresh();
// 					}
// 				},
// 			});
// 		});
// 	},
// };

frappe.listview_settings["Client SMS Log"] = {
	onload: function (listview) {
		listview.page.add_inner_button(__("Sync Logs from Server"), function () {
			frappe.call({
				method: "customer_sms.jobs.sync_sms_log.sync_sms_logs", // path to your sync function
				callback: function (r) {
					if (!r.exc) {
						frappe.msgprint(__("Logs synced successfully"));
						listview.refresh();
					}
				},
			});
		});
	},
};
