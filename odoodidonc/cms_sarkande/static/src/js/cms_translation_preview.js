/** @odoo-module **/

import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CmsTranslationPreview extends Component {
    static template = "cms_sarkande.CmsTranslationPreview";
    static props = {
        pageId: Number,
        translations: Array,
        currentLang: String,
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            pageData: null,
            blocks: [],
            highlightedBlock: null,
        });
        this.previewRef = useRef("preview");

        onMounted(() => {
            this.loadPageData();
        });
    }

    async loadPageData() {
        if (!this.props.pageId) return;

        // Load page and blocks
        const page = await this.orm.read("cms.page", [this.props.pageId], ["name", "page_title", "block_ids"]);
        if (!page || page.length === 0) return;

        const blocks = await this.orm.read("cms.block", page[0].block_ids, [
            "name", "block_type", "sequence",
            "html_content", "text_content", "heading_text",
            "hero_title", "hero_subtitle", "hero_button_text",
            "image_url", "image_alt"
        ]);

        this.state.pageData = page[0];
        this.state.blocks = blocks.sort((a, b) => a.sequence - b.sequence);
    }

    highlightBlock(blockId, fieldLabel) {
        this.state.highlightedBlock = blockId ? `${blockId}-${fieldLabel}` : null;
    }

    getBlockContent(block) {
        switch (block.block_type) {
            case 'hero':
                return `
                    <div class="hero-preview" data-block="${block.id}">
                        <h1 data-field="Hero Title">${block.hero_title || ''}</h1>
                        <p data-field="Hero Subtitle">${block.hero_subtitle || ''}</p>
                        <button data-field="Button Text">${block.hero_button_text || 'Get Started'}</button>
                    </div>
                `;
            case 'heading':
                return `<h2 data-block="${block.id}" data-field="Heading">${block.heading_text || ''}</h2>`;
            case 'text':
                return `<p data-block="${block.id}" data-field="Text Content">${block.text_content || ''}</p>`;
            case 'html':
                return `<div data-block="${block.id}" data-field="HTML Content">${block.html_content || ''}</div>`;
            case 'image':
                return `<img data-block="${block.id}" src="${block.image_url || ''}" alt="${block.image_alt || ''}" style="max-width: 100%;">`;
            case 'user_list':
                return `<div data-block="${block.id}"><em>User List (dynamic content)</em></div>`;
            default:
                return '';
        }
    }

    get previewHtml() {
        if (!this.state.blocks || this.state.blocks.length === 0) {
            return '<p style="text-align: center; padding: 20px;">Loading preview...</p>';
        }

        const content = this.state.blocks.map(block => this.getBlockContent(block)).join('\n');
        return content;
    }

    isHighlighted(blockId, fieldLabel) {
        return this.state.highlightedBlock === `${blockId}-${fieldLabel}`;
    }
}

registry.category("fields").add("cms_translation_preview", {
    component: CmsTranslationPreview,
});
