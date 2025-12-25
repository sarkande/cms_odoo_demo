{
    "name": "cms_sarkande",
    "summary": "cms",
    "version": "19.0.0.1.0",
    "category": "Uncategorized",
    "website": "https://www.example.com",
    "author": "Sarkande",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
        "iap",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/cms_page_views.xml",
        "views/cms_block_views.xml",
        "views/cms_block_component_views.xml",
        "views/cms_translation_views.xml",
        "wizard/cms_block_translate_wizard_views.xml",
        "wizard/cms_page_translate_wizard_views.xml",
        "data/cms_demo_data.xml",
        "data/cms_translation_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}