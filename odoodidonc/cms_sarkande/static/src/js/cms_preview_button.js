/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { CmsPreviewModal } from "./cms_preview_modal";

export class CmsPreviewButton extends Component {
    static template = "cms_sarkande.CmsPreviewButton";
    static props = ["*"];

    setup() {
        this.dialog = useService("dialog");
        this.orm = useService("orm");
    }

    async onClick(ev) {
        // Prevent default button behavior
        ev.preventDefault();
        ev.stopPropagation();

        // Get the current record from the form view
        const record = this.props.record;

        // Get the preview HTML - it's already computed and stored in the record
        // In Odoo 19, computed fields are accessed via record.data
        const previewHtml = record.data.preview_html || "";

        console.log("Opening preview with HTML length:", previewHtml.length);

        // Open the preview modal
        this.dialog.add(CmsPreviewModal, {
            previewHtml: previewHtml,
        });
    }
}

// Register as a widget
registry.category("view_widgets").add("cms_preview_button", CmsPreviewButton);
