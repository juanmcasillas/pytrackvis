from .impl import impl

frontend_modules = [
    impl,
]

def register_frontend(app):
    for i in frontend_modules:
        app.register_blueprint(i)
    return app