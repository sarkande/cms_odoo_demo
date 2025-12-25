from odoo import http
from odoo.http import request
from odoo.modules.module import get_module_path
import os
import mimetypes
import json

MODULE_NAME = 'cms_sarkande'

class CmsFront(http.Controller):

    def _get_content_type(self, path):
        """Détecter le type MIME basé sur l'extension du fichier"""
        content_type, _ = mimetypes.guess_type(path)
        if content_type is None:
            content_type = 'application/octet-stream'
        return content_type

    def _serve_static_file(self, relative_path):
        """Servir un fichier statique depuis le dossier front"""
        path = os.path.join(get_module_path(MODULE_NAME), 'static', 'front', relative_path)
        if not os.path.isfile(path):
            return request.not_found()

        content_type = self._get_content_type(path)
        with open(path, 'rb') as f:
            content = f.read()
        return request.make_response(content, [('Content-Type', content_type)])

    @http.route('/', type='http', auth='public', website=True)
    def index(self, **kwargs):
        # Servir index.html qui redirigera vers /home
        path = os.path.join(get_module_path(MODULE_NAME),
                            'static', 'front', 'index.html')
        with open(path, 'rb') as f:
            content = f.read()
        return request.make_response(content, [('Content-Type', 'text/html')])

    @http.route('/cms', type='http', auth='public', website=True)
    def cms_list(self, **kwargs):
        # Liste des pages CMS
        path = os.path.join(get_module_path(MODULE_NAME),
                            'static', 'front', 'cms.html')
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                content = f.read()
            return request.make_response(content, [('Content-Type', 'text/html')])
        return request.not_found()

    @http.route('/<string:slug>', type='http', auth='public', website=True)
    def serve_cms_page(self, slug, **kwargs):
        # Servir le template dynamique [slug].html pour les pages CMS
        slug_template_path = os.path.join(get_module_path(MODULE_NAME),
                                          'static', 'front', '[slug].html')

        if os.path.isfile(slug_template_path):
            with open(slug_template_path, 'rb') as f:
                content = f.read()
            return request.make_response(content, [('Content-Type', 'text/html')])

        return request.not_found()

    # Routes pour les ressources Next.js référencées depuis la racine
    @http.route('/_next/<path:page>', type='http', auth='public', website=True)
    def serve_next(self, page, **kwargs):
        return self._serve_static_file(f'_next/{page}')

    # Routes pour les fichiers statiques à la racine (favicon, images, etc.)
    @http.route(['/<string:filename>.svg', '/<string:filename>.ico',
                 '/<string:filename>.png', '/<string:filename>.jpg',
                 '/<string:filename>.jpeg', '/<string:filename>.webp'],
                type='http', auth='public', website=True)
    def serve_static_root(self, filename, **kwargs):
        # Récupérer l'extension depuis la requête
        ext = request.httprequest.path.split('.')[-1]
        return self._serve_static_file(f'{filename}.{ext}')

    # API Routes pour Next.js
    @http.route('/api/users', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def api_users(self, **kwargs):
        """Retourne la liste des utilisateurs au format JSON"""
        try:
            # Récupérer tous les utilisateurs
            users = request.env['res.users'].sudo().search([])

            # Formater les données
            users_data = []
            for user in users:
                users_data.append({
                    'id': user.id,
                    'name': user.name,
                    'login': user.login,
                    'email': user.email or '',
                    'active': user.active,
                    'company_id': user.company_id.id if user.company_id else None,
                    'company_name': user.company_id.name if user.company_id else '',
                    'image_url': f'/web/image/res.users/{user.id}/image_128' if user.image_128 else None,
                })

            response_data = {
                'success': True,
                'data': users_data,
                'count': len(users_data)
            }

            return request.make_response(
                json.dumps(response_data, ensure_ascii=False),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type')
                ]
            )
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            return request.make_response(
                json.dumps(error_response),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*')
                ],
                status=500
            )

    # CMS API Routes
    @http.route('/api/cms/pages', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def api_cms_pages(self, **kwargs):
        """Retourne la liste de toutes les pages CMS"""
        try:
            pages = request.env['cms.page'].sudo().search([('active', '=', True)])
            pages_data = [{
                'id': page.id,
                'name': page.name,
                'slug': page.slug,
                'title': page.title or page.name,
            } for page in pages]

            response_data = {
                'success': True,
                'data': pages_data,
                'count': len(pages_data)
            }

            return request.make_response(
                json.dumps(response_data, ensure_ascii=False),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type')
                ]
            )
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            return request.make_response(
                json.dumps(error_response),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*')
                ],
                status=500
            )

    @http.route('/api/cms/page/<string:slug>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def api_cms_page(self, slug, lang='en_US', **kwargs):
        """Retourne une page CMS avec tous ses blocs traduits"""
        try:
            page = request.env['cms.page'].sudo().search([('slug', '=', slug), ('active', '=', True)], limit=1)

            if not page:
                error_response = {
                    'success': False,
                    'error': f'Page "{slug}" not found'
                }
                return request.make_response(
                    json.dumps(error_response),
                    headers=[
                        ('Content-Type', 'application/json'),
                        ('Access-Control-Allow-Origin', '*')
                    ],
                    status=404
                )

            response_data = {
                'success': True,
                'data': page.get_page_data(lang=lang)
            }

            return request.make_response(
                json.dumps(response_data, ensure_ascii=False),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type')
                ]
            )
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            return request.make_response(
                json.dumps(error_response),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*')
                ],
                status=500
            )

    # Translation API Routes
    @http.route('/api/translations/<string:lang>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def api_translations(self, lang, **kwargs):
        """Retourne toutes les traductions pour une langue donnée"""
        try:
            translations = request.env['cms.translation.key'].sudo().get_translations(lang)

            response_data = {
                'success': True,
                'data': translations,
                'lang': lang
            }

            return request.make_response(
                json.dumps(response_data, ensure_ascii=False),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type')
                ]
            )
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            return request.make_response(
                json.dumps(error_response),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*')
                ],
                status=500
            )

    @http.route('/api/languages', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def api_languages(self, **kwargs):
        """Retourne la liste des langues disponibles"""
        try:
            languages = request.env['cms.translation.key'].sudo().get_available_languages()

            response_data = {
                'success': True,
                'data': languages,
                'count': len(languages)
            }

            return request.make_response(
                json.dumps(response_data, ensure_ascii=False),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type')
                ]
            )
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            return request.make_response(
                json.dumps(error_response),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*')
                ],
                status=500
            )
