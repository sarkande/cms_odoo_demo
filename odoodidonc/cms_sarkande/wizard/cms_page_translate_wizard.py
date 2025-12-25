from odoo import models, fields, api


class CmsPageTranslateWizard(models.TransientModel):
    _name = 'cms.page.translate.wizard'
    _description = 'CMS Page Translation Wizard'

    page_id = fields.Many2one('cms.page', string='Page', required=True)
    lang_id = fields.Many2one('res.lang', string='Language', required=True,
                             domain=[('active', '=', True)])

    translation_line_ids = fields.One2many('cms.page.translate.line', 'wizard_id',
                                          string='Translations')
    preview_html = fields.Html(string='Preview', compute='_compute_preview_html')

    @api.depends('page_id', 'lang_id', 'translation_line_ids.translated_value')
    def _compute_preview_html(self):
        """Generate preview HTML for the page"""
        for wizard in self:
            if not wizard.page_id:
                wizard.preview_html = '<p>No page selected</p>'
                continue

            html_parts = ['<div class="cms-page-preview">']

            for block in wizard.page_id.block_ids.sorted('sequence'):
                block_html = wizard._get_block_preview_html(block)
                if block_html:
                    html_parts.append(f'<div class="preview-block" data-block-id="{block.id}" data-block-name="{block.name}">{block_html}</div>')

            html_parts.append('</div>')
            wizard.preview_html = '\n'.join(html_parts)

    def _get_block_preview_html(self, block):
        """Generate HTML preview for a single block"""
        lang = self.lang_id.code if self.lang_id else 'en_US'

        if block.block_type == 'hero':
            title = block.hero_title_id.with_context(lang=lang).title if block.hero_title_id else ''
            subtitle = block.hero_subtitle_id.with_context(lang=lang).title if block.hero_subtitle_id else ''
            button = block.hero_button_text_id.with_context(lang=lang).title if block.hero_button_text_id else ''
            return f'''
                <div class="hero-section" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 8px; margin: 10px 0;">
                    <h1 data-field="Hero Title" style="font-size: 32px; margin: 0 0 10px 0;">{title}</h1>
                    <p data-field="Hero Subtitle" style="font-size: 16px; margin: 0 0 20px 0; opacity: 0.9;">{subtitle}</p>
                    <button data-field="Button Text" style="background: white; color: #667eea; border: none; padding: 12px 24px; border-radius: 4px; font-weight: 600;">{button}</button>
                </div>
            '''
        elif block.block_type == 'heading':
            text = block.heading_title_id.with_context(lang=lang).title if block.heading_title_id else ''
            return f'<h2 data-field="Heading" style="margin: 20px 0 10px 0;">{text}</h2>'
        elif block.block_type == 'text':
            content = block.text_component_id.with_context(lang=lang).content if block.text_component_id else ''
            return f'<p data-field="Text Content" style="margin: 10px 0;">{content}</p>'
        elif block.block_type == 'html':
            content = block.html_component_id.with_context(lang=lang).content if block.html_component_id else ''
            return f'<div data-field="HTML Content" style="margin: 10px 0;">{content}</div>'
        elif block.block_type == 'image':
            return f'<img src="{block.image_url or ""}" alt="{block.image_alt or ""}" style="max-width: 100%; margin: 10px 0;">'
        elif block.block_type == 'user_list':
            return '<div style="padding: 20px; background: #f5f5f5; margin: 10px 0;"><em>Liste d\'utilisateurs (contenu dynamique)</em></div>'

        return ''

    @api.model
    def default_get(self, fields_list):
        """Initialize with page from context"""
        res = super().default_get(fields_list)

        page_id = self.env.context.get('active_id')
        if page_id:
            res['page_id'] = page_id

            # Default to first active language (not en_US)
            lang = self.env['res.lang'].search([
                ('active', '=', True),
                ('code', '!=', 'en_US')
            ], limit=1)

            if lang:
                res['lang_id'] = lang.id
                # Load translations for this language
                page = self.env['cms.page'].browse(page_id)
                lines = self._prepare_translation_lines(page, lang.code)
                res['translation_line_ids'] = lines

        return res

    @api.onchange('lang_id')
    def _onchange_lang_id(self):
        """Reload translations when language changes"""
        if not self.page_id or not self.lang_id:
            self.translation_line_ids = [(5, 0, 0)]  # Clear all lines
            return

        # Clear existing lines first to avoid duplicates
        self.translation_line_ids = [(5, 0, 0)]

        # Then add new lines
        lines = self._prepare_translation_lines(self.page_id, self.lang_id.code)
        self.translation_line_ids = lines

    def _prepare_translation_lines(self, page, lang_code):
        """Prepare translation lines for all blocks in page"""
        lines = []

        for block in page.block_ids.sorted('sequence'):
            # Skip non-translatable blocks
            if block.block_type in ['user_list', 'image']:
                continue

            # Get translatable fields for this block
            fields_info = self._get_block_translatable_fields(block)

            for field_info in fields_info:
                # Get source value (en_US)
                source_value = self._get_field_value(
                    field_info['component'],
                    field_info['field'],
                    'en_US'
                )

                # Get translated value
                translated_value = self._get_field_value(
                    field_info['component'],
                    field_info['field'],
                    lang_code
                )

                # Detect if content is HTML (check if source contains complex HTML, not just simple wrappers)
                import re
                value_str = str(source_value).strip()

                # Remove single <p> wrapper to check if there's real HTML inside
                clean_value = re.sub(r'^<p>(.*)</p>$', r'\1', value_str, flags=re.DOTALL).strip()

                # Check if the cleaned content still has HTML tags
                is_html = bool(re.search(r'<[a-z][\s\S]*>', clean_value, re.IGNORECASE))

                lines.append((0, 0, {
                    'block_id': block.id,
                    'block_name': block.name,
                    'field_label': field_info['label'],
                    'source_value': source_value,
                    'translated_value': translated_value,
                    'component_model': field_info['component']._name,
                    'component_id': field_info['component'].id,
                    'component_field': field_info['field'],
                    'is_html_content': is_html,
                }))

        return lines

    def _get_block_translatable_fields(self, block):
        """Get translatable fields for a block"""
        fields_list = []

        if block.block_type == 'html' and block.html_component_id:
            fields_list.append({
                'label': 'HTML Content',
                'component': block.html_component_id,
                'field': 'content',
            })

        elif block.block_type == 'text' and block.text_component_id:
            fields_list.append({
                'label': 'Text Content',
                'component': block.text_component_id,
                'field': 'content',
            })

        elif block.block_type == 'heading' and block.heading_title_id:
            fields_list.append({
                'label': 'Heading',
                'component': block.heading_title_id,
                'field': 'title',
            })

        elif block.block_type == 'hero':
            if block.hero_title_id:
                fields_list.append({
                    'label': 'Hero Title',
                    'component': block.hero_title_id,
                    'field': 'title',
                })
            if block.hero_subtitle_id:
                fields_list.append({
                    'label': 'Hero Subtitle',
                    'component': block.hero_subtitle_id,
                    'field': 'title',
                })
            if block.hero_button_text_id:
                fields_list.append({
                    'label': 'Button Text',
                    'component': block.hero_button_text_id,
                    'field': 'title',
                })

        return fields_list

    def _get_field_value(self, component, field_name, lang_code):
        """Get field value in specific language"""
        if not component:
            return ''

        # Use with_context to get translated value
        record_with_lang = component.with_context(lang=lang_code)
        return record_with_lang[field_name] or ''

    def _save_translations_to_db(self):
        """Internal method to save translations to database"""
        lang_code = self.lang_id.code

        for line in self.translation_line_ids:
            translated_value = line.translated_value

            if not translated_value:
                continue

            # If the original content was NOT HTML, strip the HTML wrapper added by the widget
            if not line.is_html_content:
                # Remove wrapper tags added by Odoo HTML widget
                # e.g., <div data-oe-version="2.0">text</div> -> text
                #       <p data-oe-version="2.0">text</p> -> text
                #       <p>text</p> -> text
                import re
                from markupsafe import Markup

                # Convert Markup to string if needed
                value_str = str(translated_value)

                # Remove common wrapper patterns added by Odoo
                # Pattern 1: <div ...>content</div>
                value_str = re.sub(r'^<div[^>]*>(.*)</div>$', r'\1', value_str, flags=re.DOTALL)
                # Pattern 2: Single <p ...>content</p> wrapper (with or without attributes)
                value_str = re.sub(r'^<p[^>]*>(.*)</p>$', r'\1', value_str, flags=re.DOTALL)

                translated_value = value_str.strip()

            # Get the component record with the target language context
            component = self.env[line.component_model].browse(line.component_id)
            component_with_lang = component.with_context(lang=lang_code)

            # Write the translated value directly in the target language
            # This will create/update the translation automatically
            component_with_lang.write({
                line.component_field: translated_value
            })

    def action_save_and_refresh(self):
        """Save translations and refresh the wizard to update preview"""
        self._save_translations_to_db()

        # Return action to reload the same wizard
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cms.page.translate.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_save_translations(self):
        """Save all translations and close wizard"""
        self._save_translations_to_db()
        return {'type': 'ir.actions.act_window_close'}


class CmsPageTranslateLine(models.TransientModel):
    _name = 'cms.page.translate.line'
    _description = 'CMS Page Translation Line'
    _order = 'block_id, field_label'

    wizard_id = fields.Many2one('cms.page.translate.wizard', required=True, ondelete='cascade')

    block_id = fields.Many2one('cms.block', string='Block', readonly=True)
    block_name = fields.Char(string='Block', readonly=True)
    field_label = fields.Char(string='Field', readonly=True)

    source_value = fields.Html(string='Source (English)')
    translated_value = fields.Html(string='Translation')
    is_html_content = fields.Boolean(string='Is HTML Content', default=False)

    # Component reference
    component_model = fields.Char(string='Component Model')
    component_id = fields.Integer(string='Component ID')
    component_field = fields.Char(string='Component Field')

    @api.onchange('translated_value')
    def _onchange_translated_value(self):
        """Auto-save translation on change to update preview"""
        import logging
        _logger = logging.getLogger(__name__)

        # Skip if no translation yet
        if not self.translated_value:
            return

        # Skip if source and translated are the same (initial load)
        if self.source_value == self.translated_value:
            return

        # Only save if we have all required data
        if not (self.component_model and self.component_id and self.component_field):
            _logger.warning("Missing component data for auto-save")
            return

        # Get language from wizard_id if available
        if not self.wizard_id or not self.wizard_id.lang_id:
            _logger.warning("Missing wizard or language for auto-save")
            return

        # Save the translation immediately
        translated_value = self.translated_value

        # Clean HTML if needed
        if not self.is_html_content:
            import re
            value_str = str(translated_value)
            value_str = re.sub(r'^<div[^>]*>(.*)</div>$', r'\1', value_str, flags=re.DOTALL)
            value_str = re.sub(r'^<p[^>]*>(.*)</p>$', r'\1', value_str, flags=re.DOTALL)
            translated_value = value_str.strip()

        # Save to component
        try:
            component = self.env[self.component_model].browse(self.component_id)
            component_with_lang = component.with_context(lang=self.wizard_id.lang_id.code)
            component_with_lang.write({
                self.component_field: translated_value
            })
            _logger.info(f"Auto-saved translation for {self.component_model}({self.component_id}).{self.component_field}")
        except Exception as e:
            _logger.error(f"Error during auto-save: {e}")
            pass
