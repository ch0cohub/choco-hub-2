from core.blueprints.base_blueprint import BaseBlueprint

hubfile_bp = BaseBlueprint('hubfile', __name__, template_folder='templates')


def register_routes_hubfile():
    from app.modules.hubfile import routes  