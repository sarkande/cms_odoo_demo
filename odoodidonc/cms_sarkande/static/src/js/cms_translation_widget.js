/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";

export class CmsTranslationWidget extends Component {
    static template = "cms_sarkande.CmsTranslationWidget";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            translations: {},
            loading: false,
            currentLang: 'en_US',
        });

        this.loadTranslations();
    }

    async loadTranslations() {
        const record = this.props.record;
        const modelName = record.resModel;
        const resId = record.resId;
        const fieldName = this.props.name;

        // Get all languages
        const languages = await this.orm.searchRead(
            "res.lang",
            [["active", "=", true]],
            ["code", "name"],
        );

        // Get translations for this field
        const translations = await this.orm.call(
            modelName,
            "get_field_translations",
            [resId, fieldName],
        );

        this.state.translations = translations || {};
        this.state.languages = languages;
    }

    async translateAll() {
        this.state.loading = true;
        try {
            const record = this.props.record;
            const modelName = record.resModel;
            const resId = record.resId;
            const fieldName = this.props.name;

            await this.orm.call(
                modelName,
                "auto_translate_field",
                [resId, fieldName],
            );

            this.notification.add("Traduction automatique terminée", {
                type: "success",
            });

            await this.loadTranslations();
        } catch (error) {
            this.notification.add("Erreur lors de la traduction automatique", {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
    }

    async updateTranslation(lang, value) {
        const record = this.props.record;
        const modelName = record.resModel;
        const resId = record.resId;
        const fieldName = this.props.name;

        await this.orm.call(
            modelName,
            "update_field_translation",
            [resId, fieldName, lang, value],
        );
    }
}

registry.category("fields").add("cms_translation", CmsTranslationWidget);
