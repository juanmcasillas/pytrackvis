from .web_impl import web_impl
from .track_impl import track_impl
from .places_impl import places_impl

frontend_modules = [
    web_impl,
    track_impl,
    places_impl
]

def register_frontend(app):
    for i in frontend_modules:
        app.register_blueprint(i)
    return app