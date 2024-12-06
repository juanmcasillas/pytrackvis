from .web_impl import web_impl
from .track_impl import track_impl

frontend_modules = [
    web_impl,
    track_impl,
]

def register_frontend(app):
    for i in frontend_modules:
        app.register_blueprint(i)
    return app