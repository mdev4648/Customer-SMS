frappe.ui.form.on("Bulk SMS", {
	refresh: function (frm) {
		// nothing for now
	},

	recipients: function (frm) {
		let raw = frm.doc.recipients || "";
		// split by newline, comma, or semicolon
		let arr = raw
			.split(/[\n,;]+/)
			.map((x) => x.trim())
			.filter(Boolean);
		frm.set_value("created_count", arr.length);
	},

	// also set count on load
	onload: function (frm) {
		let raw = frm.doc.recipients || "";
		let arr = raw
			.split(/[\n,;]+/)
			.map((x) => x.trim())
			.filter(Boolean);
		frm.set_value("created_count", arr.length);
	},
});
