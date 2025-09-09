{
    "name": "AI Chat",
    "version": "1.0.0",
    "summary": "AI чат для управління завданнями",
    "author": "MTCH",
    "category": "Productivity",
    "license": "LGPL-3",
    "depends": ["web", "project"],  # наш модуль залежить від Project
    "data": [
        "view/chat_templates.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "ai_chat/static/src/js/chat_widget.js",
            "ai_chat/static/src/css/chat_styles.css",
        ],
    },
    "installable": True,
    "application": True,
}
