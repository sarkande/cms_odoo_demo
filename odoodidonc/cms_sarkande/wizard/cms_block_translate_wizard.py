from odoo import models, fields, api
from odoo.exceptions import UserError


class CmsBlockTranslateWizard(models.TransientModel):
    _name = 'cms.block.translate.wizard'
    _description = 'CMS Block Translation Wizard'

    block_id = fields.Many2one('cms.block', string='Block', required=True)
    block_type = fields.Selection(related='block_id.block_type', string='Block Type')

    # Language selection
    lang_ids = fields.Many2many('res.lang', string='Languages',
                                domain=[('active', '=', True)])

    # Translation lines - one per field per language
    translation_line_ids = fields.One2many('cms.block.translate.line', 'wizard_id',
                                          string='Translations')

    @api.model
    def default_get(self, fields_list):
        """Initialize wizard with current block and all active languages"""
        res = super().default_get(fields_list)

        # Get block from context
        block_id = self.env.context.get('active_id')
        if block_id:
            res['block_id'] = block_id

            # Get all active languages by default
            langs = self.env['res.lang'].search([('active', '=', True)])
            res['lang_ids'] = [(6, 0, langs.ids)]

            # Load translations immediately
            block = self.env['cms.block'].browse(block_id)
            lines = self._prepare_translation_lines(block, langs)
            res['translation_line_ids'] = lines

        return res

    def _prepare_translation_lines(self, block, langs):
        """Prépare les lignes de traduction"""
        lines = []

        # Récupère les champs traduisibles selon le type de bloc
        translatable_fields = self._get_translatable_fields_for_block(block)

        for field_info in translatable_fields:
            for lang in langs:
                # Récupère la valeur traduite
                value = self._get_field_translation(
                    field_info['component'],
                    field_info['field'],
                    lang.code
                )

                lines.append((0, 0, {
                    'field_name': field_info['name'],
                    'field_label': field_info['label'],
                    'lang_id': lang.id,
                    'lang_code': lang.code,
                    'value': value,
                    'component_model': field_info['component']._name,
                    'component_id': field_info['component'].id,
                    'component_field': field_info['field'],
                }))

        return lines

    @api.onchange('block_id', 'lang_ids')
    def _onchange_load_translations(self):
        """Charge toutes les traductions pour le bloc"""
        if not self.block_id:
            self.translation_line_ids = False
            return

        langs = self.lang_ids or self.env['res.lang'].search([('active', '=', True)])
        lines = self._prepare_translation_lines(self.block_id, langs)
        self.translation_line_ids = lines

    def _get_translatable_fields_for_block(self, block):
        """Retourne la liste des champs traduisibles pour ce bloc"""
        fields_list = []

        if block.block_type == 'html' and block.html_component_id:
            fields_list.append({
                'name': 'html_content',
                'label': 'HTML Content',
                'component': block.html_component_id,
                'field': 'content',
            })

        elif block.block_type == 'text' and block.text_component_id:
            fields_list.append({
                'name': 'text_content',
                'label': 'Text Content',
                'component': block.text_component_id,
                'field': 'content',
            })

        elif block.block_type == 'heading' and block.heading_title_id:
            fields_list.append({
                'name': 'heading_text',
                'label': 'Heading Text',
                'component': block.heading_title_id,
                'field': 'title',
            })

        elif block.block_type == 'hero':
            if block.hero_title_id:
                fields_list.append({
                    'name': 'hero_title',
                    'label': 'Hero Title',
                    'component': block.hero_title_id,
                    'field': 'title',
                })
            if block.hero_subtitle_id:
                fields_list.append({
                    'name': 'hero_subtitle',
                    'label': 'Hero Subtitle',
                    'component': block.hero_subtitle_id,
                    'field': 'title',
                })
            if block.hero_button_text_id:
                fields_list.append({
                    'name': 'hero_button_text',
                    'label': 'Button Text',
                    'component': block.hero_button_text_id,
                    'field': 'title',
                })

        elif block.block_type == 'image' and block.image_component_id:
            fields_list.append({
                'name': 'image_alt',
                'label': 'Image Alt Text',
                'component': block.image_component_id,
                'field': 'alt',
            })

        return fields_list

    def _get_field_translation(self, component, field_name, lang_code):
        """Récupère la traduction d'un champ"""
        if not component:
            return ''

        # Cherche dans ir.translation
        translation = self.env['ir.translation'].search([
            ('type', '=', 'model'),
            ('name', '=', f'{component._name},{field_name}'),
            ('res_id', '=', component.id),
            ('lang', '=', lang_code),
        ], limit=1)

        if translation and translation.value:
            return translation.value

        # Fallback sur la valeur du champ
        record_with_lang = component.with_context(lang=lang_code)
        return record_with_lang[field_name] or ''

    def action_save_translations(self):
        """Sauvegarde toutes les traductions"""
        for line in self.translation_line_ids:
            if line.value:
                # Cherche ou crée la traduction
                translation = self.env['ir.translation'].search([
                    ('type', '=', 'model'),
                    ('name', '=', f'{line.component_model},{line.component_field}'),
                    ('res_id', '=', line.component_id),
                    ('lang', '=', line.lang_code),
                ], limit=1)

                if translation:
                    translation.value = line.value
                else:
                    # Récupère la valeur source (en_US)
                    component = self.env[line.component_model].browse(line.component_id)
                    src_value = component[line.component_field] or ''

                    self.env['ir.translation'].create({
                        'type': 'model',
                        'name': f'{line.component_model},{line.component_field}',
                        'res_id': line.component_id,
                        'lang': line.lang_code,
                        'src': src_value,
                        'value': line.value,
                        'module': 'cms_sarkande',
                        'state': 'translated',
                    })

        return {'type': 'ir.actions.act_window_close'}


class CmsBlockTranslateLine(models.TransientModel):
    _name = 'cms.block.translate.line'
    _description = 'CMS Block Translation Line'
    _order = 'field_name, lang_code'

    wizard_id = fields.Many2one('cms.block.translate.wizard', required=True, ondelete='cascade')

    field_name = fields.Char(string='Field Name', required=True)
    field_label = fields.Char(string='Field Label', required=True)

    lang_id = fields.Many2one('res.lang', string='Language', required=True)
    lang_code = fields.Char(string='Language Code', required=True)
    lang_name = fields.Char(related='lang_id.name', string='Language Name')

    value = fields.Text(string='Translation')

    # Référence au composant
    component_model = fields.Char(string='Component Model')
    component_id = fields.Integer(string='Component ID')
    component_field = fields.Char(string='Component Field')
