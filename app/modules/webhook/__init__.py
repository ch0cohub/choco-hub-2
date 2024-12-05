from core.blueprints.base_blueprint import BaseBlueprint

webhook_bp = BaseBlueprint('webhook', __name__, template_folder='templates')


def register_routes_webhook():
    from app.modules.webhook import routes  
