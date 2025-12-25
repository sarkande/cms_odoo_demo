from odoo import models, fields


class CmsBlockTitle(models.Model):
    """Composant titre - réutilisable avec translate=True"""
    _name = 'cms.block.title'
    _inherit = ['cms.translation.mixin']
    _description = 'CMS Block Title Component'

    title = fields.Char(string='Title', translate=True)


class CmsBlockText(models.Model):
    """Composant texte - réutilisable avec translate=True"""
    _name = 'cms.block.text'
    _inherit = ['cms.translation.mixin']
    _description = 'CMS Block Text Component'

    content = fields.Text(string='Text Content', translate=True)


class CmsBlockHtml(models.Model):
    """Composant HTML - réutilisable avec translate=True"""
    _name = 'cms.block.html'
    _inherit = ['cms.translation.mixin']
    _description = 'CMS Block HTML Component'

    content = fields.Html(string='HTML Content', translate=True)


class CmsBlockImage(models.Model):
    """Composant image - avec alt text traduit"""
    _name = 'cms.block.image'
    _inherit = ['cms.translation.mixin']
    _description = 'CMS Block Image Component'

    url = fields.Char(string='Image URL', required=True)
    alt = fields.Char(string='Alt Text', translate=True)
