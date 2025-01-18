from flask import Blueprint


def setup_routes(app):
    from app.routes.sections import sections
    from app.routes.task import task
    from app.routes.user import user
    from app.routes.main import main

    app.register_blueprint(main)
    app.register_blueprint(user)
    app.register_blueprint(sections)
    app.register_blueprint(task)
