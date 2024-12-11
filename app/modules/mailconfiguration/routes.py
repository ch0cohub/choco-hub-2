from flask import render_template
from app.modules.mailconfiguration import mailconfiguration_bp


@mailconfiguration_bp.route('/mailconfiguration', methods=['GET'])
def index():
    return render_template('mailconfiguration/index.html')
