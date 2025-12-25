from odoo import models, fields, api


class CmsPage(models.Model):
    _name = 'cms.page'
    _description = 'CMS Page'
    _order = 'sequence, id'

    name = fields.Char(string='Page Name', required=True)
    slug = fields.Char(string='URL Slug', required=True, index=True,
                       help='URL-friendly identifier (e.g., "home", "about-us")')
    title = fields.Char(string='Page Title', help='Title displayed in browser')
    meta_description = fields.Text(string='Meta Description')
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', default=10)

    block_ids = fields.One2many('cms.block', 'page_id', string='Blocks')

    _sql_constraints = [
        ('slug_unique', 'UNIQUE(slug)', 'The URL slug must be unique!')
    ]

    def action_open_translate_wizard(self):
        """Open translation wizard for this page"""
        self.ensure_one()
        return {
            'name': 'Traduire la page',
            'type': 'ir.actions.act_window',
            'res_model': 'cms.page.translate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_page_id': self.id},
        }

    def get_page_data(self, lang='en_US'):
        """Return page data formatted for API consumption with translations"""
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'title': self.title or self.name,
            'meta_description': self.meta_description or '',
            'blocks': [block.get_block_data(lang=lang) for block in self.block_ids.sorted('sequence')]
        }
