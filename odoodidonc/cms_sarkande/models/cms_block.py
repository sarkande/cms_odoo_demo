from odoo import models, fields, api


class CmsBlock(models.Model):
    _name = 'cms.block'
    _description = 'CMS Block'
    _order = 'sequence, id'

    name = fields.Char(string='Block Name', required=True)
    page_id = fields.Many2one('cms.page', string='Page', required=True, ondelete='cascade')
    block_type = fields.Selection([
        ('html', 'HTML Content'),
        ('text', 'Plain Text'),
        ('heading', 'Heading'),
        ('image', 'Image'),
        ('user_list', 'User List'),
        ('hero', 'Hero Section'),
    ], string='Block Type', required=True, default='text')

    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)

    # Component references (content with translations)
    html_component_id = fields.Many2one('cms.block.html', string='HTML Component', ondelete='cascade')
    text_component_id = fields.Many2one('cms.block.text', string='Text Component', ondelete='cascade')

    # Heading components
    heading_title_id = fields.Many2one('cms.block.title', string='Heading', ondelete='cascade')
    heading_level = fields.Selection([
        ('h1', 'H1'),
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4'),
    ], string='Heading Level', default='h2')

    # Image component
    image_component_id = fields.Many2one('cms.block.image', string='Image Component', ondelete='cascade')

    # Hero section components
    hero_title_id = fields.Many2one('cms.block.title', string='Hero Title', ondelete='cascade')
    hero_subtitle_id = fields.Many2one('cms.block.title', string='Hero Subtitle', ondelete='cascade')
    hero_button_text_id = fields.Many2one('cms.block.title', string='Button Text', ondelete='cascade')
    hero_button_url = fields.Char(string='Button URL')
    hero_background_image = fields.Char(string='Background Image URL')

    # Dynamic content config
    limit = fields.Integer(string='Limit', default=10,
                          help='Number of items to display for dynamic blocks')

    # Related fields for easier editing (these are the actual translatable fields)
    html_content = fields.Html(related='html_component_id.content', string='HTML Content', readonly=False, store=False)
    text_content = fields.Text(related='text_component_id.content', string='Text Content', readonly=False, store=False)
    heading_text = fields.Char(related='heading_title_id.title', string='Heading Text', readonly=False, store=False)
    image_url = fields.Char(related='image_component_id.url', string='Image URL', readonly=False, store=False)
    image_alt = fields.Char(related='image_component_id.alt', string='Alt Text', readonly=False, store=False)
    hero_title = fields.Char(related='hero_title_id.title', string='Hero Title', readonly=False, store=False)
    hero_subtitle = fields.Char(related='hero_subtitle_id.title', string='Hero Subtitle', readonly=False, store=False)
    hero_button_text = fields.Char(related='hero_button_text_id.title', string='Button Text', readonly=False, store=False)

    @api.onchange('block_type')
    def _onchange_block_type(self):
        """Auto-create component records when block type changes"""
        if self.block_type == 'html' and not self.html_component_id:
            self.html_component_id = self.env['cms.block.html'].create({})
        elif self.block_type == 'text' and not self.text_component_id:
            self.text_component_id = self.env['cms.block.text'].create({})
        elif self.block_type == 'heading' and not self.heading_title_id:
            self.heading_title_id = self.env['cms.block.title'].create({})
        elif self.block_type == 'image' and not self.image_component_id:
            self.image_component_id = self.env['cms.block.image'].create({})
        elif self.block_type == 'hero':
            if not self.hero_title_id:
                self.hero_title_id = self.env['cms.block.title'].create({})
            if not self.hero_subtitle_id:
                self.hero_subtitle_id = self.env['cms.block.title'].create({})
            if not self.hero_button_text_id:
                self.hero_button_text_id = self.env['cms.block.title'].create({})

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-create components when creating blocks"""
        for vals in vals_list:
            block_type = vals.get('block_type')
            if block_type == 'html' and 'html_component_id' not in vals:
                vals['html_component_id'] = self.env['cms.block.html'].create({}).id
            elif block_type == 'text' and 'text_component_id' not in vals:
                vals['text_component_id'] = self.env['cms.block.text'].create({}).id
            elif block_type == 'heading' and 'heading_title_id' not in vals:
                vals['heading_title_id'] = self.env['cms.block.title'].create({}).id
            elif block_type == 'image' and 'image_component_id' not in vals:
                vals['image_component_id'] = self.env['cms.block.image'].create({}).id
            elif block_type == 'hero':
                if 'hero_title_id' not in vals:
                    vals['hero_title_id'] = self.env['cms.block.title'].create({}).id
                if 'hero_subtitle_id' not in vals:
                    vals['hero_subtitle_id'] = self.env['cms.block.title'].create({}).id
                if 'hero_button_text_id' not in vals:
                    vals['hero_button_text_id'] = self.env['cms.block.title'].create({}).id
        return super().create(vals_list)

    def get_block_data(self, lang='en_US'):
        """Return block data formatted for API consumption with translations"""
        self.ensure_one()

        # Set context language for translate=True fields
        record = self.with_context(lang=lang)

        base_data = {
            'id': record.id,
            'name': record.name,
            'type': record.block_type,
            'sequence': record.sequence,
        }

        # Add type-specific data (translations handled by translate=True on components)
        if record.block_type == 'html':
            base_data['content'] = record.html_component_id.content if record.html_component_id else ''

        elif record.block_type == 'text':
            base_data['content'] = record.text_component_id.content if record.text_component_id else ''

        elif record.block_type == 'heading':
            base_data['text'] = record.heading_title_id.title if record.heading_title_id else ''
            base_data['level'] = record.heading_level or 'h2'

        elif record.block_type == 'image':
            if record.image_component_id:
                base_data['url'] = record.image_component_id.url or ''
                base_data['alt'] = record.image_component_id.alt or ''
            else:
                base_data['url'] = ''
                base_data['alt'] = ''

        elif record.block_type == 'hero':
            base_data['title'] = record.hero_title_id.title if record.hero_title_id else ''
            base_data['subtitle'] = record.hero_subtitle_id.title if record.hero_subtitle_id else ''
            base_data['buttonText'] = record.hero_button_text_id.title if record.hero_button_text_id else ''
            base_data['buttonUrl'] = record.hero_button_url or ''
            base_data['backgroundImage'] = record.hero_background_image or ''

        elif record.block_type == 'user_list':
            # Fetch dynamic user data
            users = record.env['res.users'].sudo().search([], limit=record.limit)
            base_data['users'] = [{
                'id': user.id,
                'name': user.name,
                'login': user.login,
                'email': user.email or '',
                'active': user.active,
            } for user in users]
            base_data['limit'] = record.limit

        return base_data
