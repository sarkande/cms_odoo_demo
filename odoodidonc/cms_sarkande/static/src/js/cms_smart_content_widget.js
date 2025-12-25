/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { HtmlField } from "@web/views/fields/html/html_field";

// Smart content widget that automatically detects if content is HTML or plain text
registry.category("fields").add("cms_smart_content", {
    component(props) {
        const value = props.record.data[props.name] || "";
        // Check if content contains HTML tags
        const isHtml = /<[a-z][\s\S]*>/i.test(value);
        return isHtml ? HtmlField : CharField;
    },
});
