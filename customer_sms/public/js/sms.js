frappe.ui.form.on("sms", {
	onload: function (frm) {
		// Listen for failed SMS from server
		frappe.realtime.on("sms_status_update", (data) => {
			if (data.status === "Failed") {
				frappe.msgprint({
					message: __("SMS to {0} FAILED. Please try resending.", [data.phone]),
					indicator: "red",
					title: __("SMS Delivery Failed"),
				});
			}
		});
	},
});

// Also listen globally for list views (optional)
frappe.ready(function () {
	frappe.realtime.on("sms_status_update", (data) => {
		if (data.status === "Failed") {
			frappe.show_alert(
				{
					message: __("SMS to {0} FAILED.", [data.phone]),
					indicator: "red",
				},
				5
			);
		}
	});
});
