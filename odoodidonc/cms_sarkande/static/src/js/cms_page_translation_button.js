/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { CmsTranslationModal } from "./cms_translation_modal";

export function openTranslationModal(component, record) {
    const dialog = component.env.services.dialog;
    dialog.add(CmsTranslationModal, {
        pageId: record.resId,
        pageName: record.data.name || "Page",
    });
}

// Register as a view button action
registry.category("view_button_registry").add("cms_open_translation_modal", {
    async onClick({ component, record }) {
        openTranslationModal(component, record);
    },
});
