from odoo import models, api
from odoo.exceptions import UserError


class CmsTranslationMixin(models.AbstractModel):
    """Mixin pour gérer la traduction automatique via IAP"""
    _name = 'cms.translation.mixin'
    _description = 'CMS Translation Mixin'

    @api.model
    def get_field_translations(self, res_id, field_name):
        """Retourne toutes les traductions d'un champ pour toutes les langues actives"""
        record = self.browse(res_id)
        if not record.exists():
            return {}

        # Get all active languages
        languages = self.env['res.lang'].search([('active', '=', True)])
        translations = {}

        for lang in languages:
            # Get translation from ir.translation table
            translation = self.env['ir.translation'].search([
                ('type', '=', 'model'),
                ('name', '=', f'{self._name},{field_name}'),
                ('res_id', '=', res_id),
                ('lang', '=', lang.code),
            ], limit=1)

            if translation:
                translations[lang.code] = translation.value
            else:
                # Fallback to default value (usually en_US)
                record_with_lang = record.with_context(lang=lang.code)
                translations[lang.code] = record_with_lang[field_name] or ''

        return translations

    @api.model
    def update_field_translation(self, res_id, field_name, lang, value):
        """Met à jour une traduction pour un champ"""
        record = self.browse(res_id)
        if not record.exists():
            raise UserError("Record not found")

        # Update or create translation
        translation = self.env['ir.translation'].search([
            ('type', '=', 'model'),
            ('name', '=', f'{self._name},{field_name}'),
            ('res_id', '=', res_id),
            ('lang', '=', lang),
        ], limit=1)

        if translation:
            translation.value = value
        else:
            self.env['ir.translation'].create({
                'type': 'model',
                'name': f'{self._name},{field_name}',
                'res_id': res_id,
                'lang': lang,
                'src': record[field_name],  # Source value (en_US)
                'value': value,
                'module': 'cms_sarkande',
                'state': 'translated',
            })

        return True

    def auto_translate_field(self, res_id=None, field_name=None):
        """Traduit automatiquement un champ via IAP (Google Translate)"""
        # Support both API call and button click
        if res_id is None:
            record = self
            field_name = self.env.context.get('field_name')
        else:
            record = self.browse(res_id)

        if not record.exists():
            raise UserError("Record not found")

        # Get source text (default language)
        source_text = record[field_name]
        if not source_text:
            raise UserError("No content to translate")

        # Get all active languages except source
        languages = self.env['res.lang'].search([
            ('active', '=', True),
            ('code', '!=', 'en_US'),
        ])

        # Get IAP account for translation
        try:
            iap_account = self.env['iap.account'].get('translation')
        except Exception:
            raise UserError(
                "Service de traduction non configuré. "
                "Vérifiez votre compte IAP dans les paramètres."
            )

        for lang in languages:
            try:
                # Call IAP translation service
                params = {
                    'texts': [source_text],
                    'source_language': 'en',
                    'target_language': self._get_iap_lang_code(lang.code),
                }

                result = iap_account.call('translator_translate', params)
                translated_text = result[0] if result else source_text

                # Store translation
                self.update_field_translation(record.id, field_name, lang.code, translated_text)

            except Exception as e:
                # Log error but continue with other languages
                self.env['ir.logging'].create({
                    'name': 'cms_translation',
                    'type': 'server',
                    'level': 'warning',
                    'message': f'Failed to translate to {lang.name}: {str(e)}',
                    'path': f'{self._name}.auto_translate_field',
                })

        return True

    @staticmethod
    def _get_iap_lang_code(odoo_lang_code):
        """Convertit un code langue Odoo en code langue IAP"""
        # Map Odoo language codes to IAP/Google Translate codes
        mapping = {
            'en_US': 'en',
            'fr_FR': 'fr',
            'de_DE': 'de',
            'es_ES': 'es',
            'it_IT': 'it',
            'pt_BR': 'pt',
            'pt_PT': 'pt',
            'nl_NL': 'nl',
            'ru_RU': 'ru',
            'ja_JP': 'ja',
            'zh_CN': 'zh-CN',
            'zh_TW': 'zh-TW',
            'ko_KR': 'ko',
            'ar_001': 'ar',
            'tr_TR': 'tr',
            'pl_PL': 'pl',
            'sv_SE': 'sv',
            'da_DK': 'da',
            'fi_FI': 'fi',
            'no_NO': 'no',
            'cs_CZ': 'cs',
            'hu_HU': 'hu',
            'ro_RO': 'ro',
            'uk_UA': 'uk',
            'vi_VN': 'vi',
            'th_TH': 'th',
            'id_ID': 'id',
            'ms_MY': 'ms',
        }

        # Extract base language code (e.g., 'fr' from 'fr_FR')
        base_code = odoo_lang_code.split('_')[0]

        return mapping.get(odoo_lang_code, base_code)
