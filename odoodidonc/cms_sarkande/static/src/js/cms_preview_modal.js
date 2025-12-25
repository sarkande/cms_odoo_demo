/** @odoo-module **/

import { Component, useState, onMounted, useRef, markup } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class CmsPreviewModal extends Component {
    static template = "cms_sarkande.CmsPreviewModal";
    static components = { Dialog };
    static props = {
        previewHtml: String,
        close: Function,
    };

    setup() {
        this.iframeRef = useRef("iframe");

        onMounted(() => {
            this.updateIframe();
        });
    }

    updateIframe() {
        const iframe = this.iframeRef.el;
        if (!iframe) return;

        const styles = `
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
                    padding: 20px;
                    margin: 0;
                }
                [data-field]:hover {
                    outline: 2px solid #4a90e2 !important;
                    background-color: #f0f8ff !important;
                }
                .hero-section {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 60px 40px;
                    text-align: center;
                    border-radius: 12px;
                    margin: 20px 0;
                }
            </style>
        `;

        const fullHtml = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                ${styles}
            </head>
            <body>
                ${this.props.previewHtml}
            </body>
            </html>
        `;

        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        iframeDoc.open();
        iframeDoc.write(fullHtml);
        iframeDoc.close();
    }
}
