/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";

export class CmsPreviewIframe extends Component {
    static template = "cms_sarkande.CmsPreviewIframe";
    static props = ["*"];

    setup() {
        this.iframeRef = useRef("iframe");
        this.highlightStyle = `
            <style>
                [data-field]:hover {
                    outline: 2px solid #4a90e2 !important;
                    background-color: #f0f8ff !important;
                    cursor: pointer;
                }
                [data-field].highlighted {
                    outline: 3px solid #ff9800 !important;
                    background-color: #fffbcc !important;
                    animation: pulse 0.5s ease-in-out;
                }
                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                }
                .cms-page-preview {
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
                }
                .preview-block {
                    margin: 10px 0;
                }
            </style>
        `;

        onMounted(() => {
            setTimeout(() => {
                this.updateIframe();
                this.setupHoverListeners();
                this.setupFieldChangeListeners();
            }, 100);
        });

        onWillUnmount(() => {
            this.removeHoverListeners();
            this.removeFieldChangeListeners();
        });
    }

    setupFieldChangeListeners() {
        // Listen to changes on translation fields to update preview
        const form = this.iframeRef.el?.closest('form');
        if (!form) return;

        // Use MutationObserver to detect DOM changes in the translation list
        this._observer = new MutationObserver((mutations) => {
            // Debounce the update
            clearTimeout(this._updateTimeout);
            this._updateTimeout = setTimeout(() => {
                this.updateIframe();
            }, 500);
        });

        const translationList = form.querySelector('.o_field_one2many');
        if (translationList) {
            this._observer.observe(translationList, {
                childList: true,
                subtree: true,
                characterData: true,
            });
        }
    }

    removeFieldChangeListeners() {
        if (this._observer) {
            this._observer.disconnect();
        }
        if (this._updateTimeout) {
            clearTimeout(this._updateTimeout);
        }
    }

    updateIframe() {
        const iframe = this.iframeRef.el;
        if (!iframe) return;

        const fieldName = this.props.name || 'preview_html';
        const htmlContent = (this.props.record && this.props.record.data && this.props.record.data[fieldName]) || '<p style="text-align: center; padding: 20px;">Loading preview...</p>';
        const fullHtml = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                ${this.highlightStyle}
            </head>
            <body>
                ${htmlContent}
            </body>
            </html>
        `;

        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        iframeDoc.open();
        iframeDoc.write(fullHtml);
        iframeDoc.close();
    }

    setupHoverListeners() {
        // Use event delegation for better performance
        const wizardForm = this.iframeRef.el?.closest('.o_cms_translation_wizard');
        if (!wizardForm) return;

        const translationList = wizardForm.querySelector('.o_field_one2many');
        if (!translationList) return;

        this._boundRowHover = this.onRowHover.bind(this);
        this._boundRowLeave = this.onRowLeave.bind(this);

        translationList.addEventListener('mouseover', this._boundRowHover);
        translationList.addEventListener('mouseout', this._boundRowLeave);

        this._translationList = translationList;
    }

    removeHoverListeners() {
        if (!this._translationList) return;

        this._translationList.removeEventListener('mouseover', this._boundRowHover);
        this._translationList.removeEventListener('mouseout', this._boundRowLeave);
    }

    onRowHover(event) {
        const row = event.target.closest('.o_data_row');
        if (!row) return;

        const blockNameCell = row.querySelector('[name="block_name"]');
        const fieldLabelCell = row.querySelector('[name="field_label"]');

        const blockName = blockNameCell?.innerText || blockNameCell?.querySelector('input')?.value;
        const fieldLabel = fieldLabelCell?.innerText || fieldLabelCell?.querySelector('input')?.value;

        if (!blockName || !fieldLabel) return;

        this.highlightElement(blockName, fieldLabel);
    }

    onRowLeave(event) {
        const row = event.target.closest('.o_data_row');
        if (!row) return;

        this.clearHighlight();
    }

    highlightElement(blockName, fieldLabel) {
        const iframe = this.iframeRef.el;
        if (!iframe) return;

        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        if (!iframeDoc) return;

        // Clear previous highlight
        this.clearHighlight();

        // Find and highlight the element
        const blocks = iframeDoc.querySelectorAll(`[data-block-name="${blockName}"]`);
        blocks.forEach(block => {
            const field = block.querySelector(`[data-field="${fieldLabel}"]`);
            if (field) {
                field.classList.add('highlighted');
                field.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }

    clearHighlight() {
        const iframe = this.iframeRef.el;
        if (!iframe) return;

        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        if (!iframeDoc) return;

        const highlighted = iframeDoc.querySelectorAll('.highlighted');
        highlighted.forEach(el => el.classList.remove('highlighted'));
    }
}

registry.category("fields").add("cms_preview_iframe", {
    component: CmsPreviewIframe,
});
