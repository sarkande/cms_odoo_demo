from odoo import models, fields, api


class CmsTranslationKey(models.Model):
    _name = 'cms.translation.key'
    _description = 'CMS Translation Key'
    _order = 'key'

    key = fields.Char(string='Translation Key', required=True, index=True,
                     help='Unique key for this translation (e.g., "nav.home", "block.team_members")')
    description = fields.Char(string='Description', help='Description of what this key is used for')
    line_ids = fields.One2many('cms.translation.line', 'translation_key_id', string='Translations')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('key_unique', 'UNIQUE(key)', 'This translation key already exists!')
    ]

    @api.model
    def get_translations(self, lang='en_US'):
        """Return all translations for a given language as a dictionary"""
        keys = self.search([('active', '=', True)])
        translations = {}

        for key in keys:
            # Chercher la ligne de traduction pour cette langue
            line = key.line_ids.filtered(lambda l: l.lang == lang and l.active)
            if line:
                translations[key.key] = line[0].value
            else:
                # Fallback sur l'anglais si la traduction n'existe pas
                fallback_line = key.line_ids.filtered(lambda l: l.lang == 'en_US' and l.active)
                if fallback_line:
                    translations[key.key] = fallback_line[0].value
                else:
                    translations[key.key] = key.key  # Dernier recours : la clé elle-même

        return translations

    @api.model
    def get_available_languages(self):
        """Return list of languages that have translations"""
        langs = self.env['res.lang'].search([('active', '=', True)])
        return [{
            'code': lang.code,
            'name': lang.name,
            'iso_code': lang.iso_code,
        } for lang in langs]


class CmsTranslationLine(models.Model):
    _name = 'cms.translation.line'
    _description = 'CMS Translation Line'
    _order = 'lang_id'

    translation_key_id = fields.Many2one('cms.translation.key', string='Translation Key', required=True, ondelete='cascade')
    lang_id = fields.Many2one('res.lang', string='Language', required=True, domain=[('active', '=', True)])
    lang = fields.Char(related='lang_id.code', string='Language Code', store=True, readonly=True)
    value = fields.Text(string='Translation', required=True)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('key_lang_unique', 'UNIQUE(translation_key_id, lang_id)', 'A translation for this language already exists for this key!')
    ]
