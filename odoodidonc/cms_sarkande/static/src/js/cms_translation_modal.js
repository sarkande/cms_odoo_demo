/** @odoo-module **/

import { Component, useState, onMounted, useRef, markup } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { HtmlField } from "@web/views/fields/html/html_field";

export class CmsTranslationModal extends Component {
    static template = "cms_sarkande.CmsTranslationModal";
    static components = { Dialog, HtmlField };
    static props = {
        pageId: Number,
        pageName: String,
        close: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            languages: [],
            selectedLang: null,
            translations: [],
            previewHtml: markup("<p>Loading...</p>"),
            highlightedIndex: null,
        });

        this.previewRef = useRef("preview");

        onMounted(() => {
            this.loadLanguages();
        });
    }

    async loadLanguages() {
        const languages = await this.orm.searchRead(
            "res.lang",
            [["active", "=", true], ["code", "!=", "en_US"]],
            ["code", "name"]
        );
        this.state.languages = languages;
        if (languages.length > 0) {
            this.state.selectedLang = languages[0].code;
            await this.loadTranslations();
        }
    }

    async onLanguageChange(ev) {
        this.state.selectedLang = ev.target.value;
        await this.loadTranslations();
    }

    async loadTranslations() {
        if (!this.state.selectedLang) return;

        // Load page blocks
        const page = await this.orm.read("cms.page", [this.props.pageId], ["block_ids"]);
        const blockIds = page[0].block_ids;

        const blocks = await this.orm.read("cms.block", blockIds, [
            "name", "block_type", "sequence",
            "html_component_id", "text_component_id", "heading_title_id",
            "hero_title_id", "hero_subtitle_id", "hero_button_text_id"
        ]);

        // Prepare translation lines
        const translations = [];
        for (const block of blocks.sort((a, b) => a.sequence - b.sequence)) {
            if (["user_list", "image"].includes(block.block_type)) continue;

            const fields = this.getBlockTranslatableFields(block);
            for (const field of fields) {
                const sourceValue = await this.getFieldValue(field.componentId, field.componentModel, field.field, "en_US");
                const translatedValue = await this.getFieldValue(field.componentId, field.componentModel, field.field, this.state.selectedLang);

                translations.push({
                    blockId: block.id,
                    blockName: block.name,
                    fieldLabel: field.label,
                    sourceValue: sourceValue || "",
                    translatedValue: translatedValue || "",
                    componentModel: field.componentModel,
                    componentId: field.componentId,
                    componentField: field.field,
                    isHtml: this.isHtmlContent(sourceValue),
                });
            }
        }

        this.state.translations = translations;
        await this.updatePreview();
    }

    getBlockTranslatableFields(block) {
        const fields = [];

        if (block.block_type === "html" && block.html_component_id) {
            fields.push({ label: "HTML Content", componentModel: "cms.block.html", componentId: block.html_component_id[0], field: "content" });
        } else if (block.block_type === "text" && block.text_component_id) {
            fields.push({ label: "Text Content", componentModel: "cms.block.text", componentId: block.text_component_id[0], field: "content" });
        } else if (block.block_type === "heading" && block.heading_title_id) {
            fields.push({ label: "Heading", componentModel: "cms.block.title", componentId: block.heading_title_id[0], field: "title" });
        } else if (block.block_type === "hero") {
            if (block.hero_title_id) fields.push({ label: "Hero Title", componentModel: "cms.block.title", componentId: block.hero_title_id[0], field: "title" });
            if (block.hero_subtitle_id) fields.push({ label: "Hero Subtitle", componentModel: "cms.block.title", componentId: block.hero_subtitle_id[0], field: "title" });
            if (block.hero_button_text_id) fields.push({ label: "Button Text", componentModel: "cms.block.title", componentId: block.hero_button_text_id[0], field: "title" });
        }

        return fields;
    }

    async getFieldValue(componentId, componentModel, fieldName, lang) {
        const records = await this.orm.read(
            componentModel,
            [componentId],
            [fieldName],
            { context: { lang: lang } }
        );
        return records[0]?.[fieldName] || "";
    }

    isHtmlContent(value) {
        if (!value) return false;
        const strValue = String(value).trim();
        const clean = strValue.replace(/^<p[^>]*>(.*)<\/p>$/s, "$1").trim();
        return /<[a-z][\s\S]*>/i.test(clean);
    }

    async onTranslationChange(index, ev) {
        const translation = this.state.translations[index];
        let value = ev.target.value || ev.detail?.value || "";

        // Clean HTML wrappers for non-HTML content
        if (!translation.isHtml && value) {
            value = value.replace(/^<div[^>]*>(.*)<\/div>$/s, "$1");
            value = value.replace(/^<p[^>]*>(.*)<\/p>$/s, "$1");
            value = value.trim();
        }

        translation.translatedValue = value;

        // Auto-save
        await this.saveTranslation(translation);
        await this.updatePreview();
    }

    async saveTranslation(translation) {
        try {
            await this.orm.write(
                translation.componentModel,
                [translation.componentId],
                { [translation.componentField]: translation.translatedValue },
                { context: { lang: this.state.selectedLang } }
            );
        } catch (error) {
            console.error("Error saving translation:", error);
        }
    }

    async updatePreview() {
        const htmlParts = ['<div class="cms-page-preview">'];

        for (const translation of this.state.translations) {
            const content = await this.getFieldValue(
                translation.componentId,
                translation.componentModel,
                translation.componentField,
                this.state.selectedLang
            );

            const html = this.getPreviewHtml(translation, content);
            htmlParts.push(`<div class="preview-block" data-block="${translation.blockName}" data-field="${translation.fieldLabel}">${html}</div>`);
        }

        htmlParts.push('</div>');
        this.state.previewHtml = markup(htmlParts.join('\n'));
    }

    getPreviewHtml(translation, content) {
        if (translation.fieldLabel === "Hero Title") {
            return `<h1 style="font-size: 32px; color: white;">${content}</h1>`;
        } else if (translation.fieldLabel === "Hero Subtitle") {
            return `<p style="font-size: 16px; color: white; opacity: 0.9;">${content}</p>`;
        } else if (translation.fieldLabel === "Button Text") {
            return `<button style="background: white; color: #667eea; border: none; padding: 12px 24px; border-radius: 4px;">${content}</button>`;
        } else if (translation.fieldLabel === "Heading") {
            return `<h2 style="margin: 20px 0 10px 0;">${content}</h2>`;
        } else if (translation.fieldLabel.includes("HTML")) {
            return `<div>${content}</div>`;
        } else {
            return `<p>${content}</p>`;
        }
    }

    onRowHover(index) {
        this.state.highlightedIndex = index;

        // Highlight in preview
        const translation = this.state.translations[index];
        const iframe = this.previewRef.el;
        if (!iframe) return;

        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        if (!iframeDoc) return;

        // Clear previous highlights
        iframeDoc.querySelectorAll('.highlighted').forEach(el => el.classList.remove('highlighted'));

        // Add highlight
        const element = iframeDoc.querySelector(`[data-block="${translation.blockName}"][data-field="${translation.fieldLabel}"]`);
        if (element) {
            element.classList.add('highlighted');
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    onRowLeave() {
        this.state.highlightedIndex = null;

        const iframe = this.previewRef.el;
        if (!iframe) return;

        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        if (!iframeDoc) return;

        iframeDoc.querySelectorAll('.highlighted').forEach(el => el.classList.remove('highlighted'));
    }

    async onSave() {
        this.notification.add("Traductions sauvegardées", { type: "success" });
        this.props.close();
    }

    getFieldProps(translation, index) {
        return {
            type: "html",
            name: `translated_value_${index}`,
            record: {
                data: {
                    [`translated_value_${index}`]: translation.translatedValue,
                },
                update: async (changes) => {
                    if (changes[`translated_value_${index}`] !== undefined) {
                        await this.onTranslationChange(index, { detail: { value: changes[`translated_value_${index}`] } });
                    }
                },
            },
            readonly: false,
        };
    }
}
