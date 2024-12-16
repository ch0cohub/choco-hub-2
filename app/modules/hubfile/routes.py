from datetime import datetime, timezone
import os
import uuid
from flask import current_app, jsonify, make_response, request, send_from_directory
from flask_login import current_user
from app.modules.hubfile import hubfile_bp
from app.modules.hubfile.models import HubfileDownloadRecord, HubfileViewRecord
from app.modules.hubfile.services import HubfileDownloadRecordService, HubfileService
from flamapy.metamodels.fm_metamodel.transformations import (
    UVLReader,
    GlencoeWriter,
    SPLOTWriter,
)
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat, DimacsWriter
import tempfile


from app import db


@hubfile_bp.route("/file/download/<int:file_id>", methods=["GET"])
def download_file(file_id):
    file = HubfileService().get_or_404(file_id)
    filename = file.name

    directory_path = f"uploads/user_{file.feature_model.data_set.user_id}/dataset_{file.feature_model.data_set_id}/"
    parent_directory_path = os.path.dirname(current_app.root_path)
    file_path = os.path.join(parent_directory_path, directory_path)

    # Get the cookie from the request or generate a new one if it does not exist
    user_cookie = request.cookies.get("file_download_cookie")
    if not user_cookie:
        user_cookie = str(uuid.uuid4())

    # Check if the download record already exists for this cookie
    existing_record = HubfileDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        file_id=file_id,
        download_cookie=user_cookie,
    ).first()

    if not existing_record:
        # Record the download in your database
        HubfileDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            file_id=file_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    # Save the cookie to the user's browser
    resp = make_response(
        send_from_directory(directory=file_path, path=filename, as_attachment=True)
    )
    resp.set_cookie("file_download_cookie", user_cookie)

    return resp


@hubfile_bp.route("/file/view/<int:file_id>", methods=["GET"])
def view_file(file_id):
    file = HubfileService().get_or_404(file_id)
    filename = file.name

    directory_path = f"uploads/user_{file.feature_model.data_set.user_id}/dataset_{file.feature_model.data_set_id}/"
    parent_directory_path = os.path.dirname(current_app.root_path)
    file_path = os.path.join(parent_directory_path, directory_path, filename)

    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()

            user_cookie = request.cookies.get("view_cookie")
            if not user_cookie:
                user_cookie = str(uuid.uuid4())

            # Check if the view record already exists for this cookie
            existing_record = HubfileViewRecord.query.filter_by(
                user_id=current_user.id if current_user.is_authenticated else None,
                file_id=file_id,
                view_cookie=user_cookie,
            ).first()

            if not existing_record:
                # Register file view
                new_view_record = HubfileViewRecord(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    file_id=file_id,
                    view_date=datetime.now(),
                    view_cookie=user_cookie,
                )
                db.session.add(new_view_record)
                db.session.commit()

            # Prepare response
            response = jsonify({"success": True, "content": content})
            if not request.cookies.get("view_cookie"):
                response = make_response(response)
                response.set_cookie(
                    "view_cookie", user_cookie, max_age=60 * 60 * 24 * 365 * 2
                )

            return response
        else:
            return jsonify({"success": False, "error": "File not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@hubfile_bp.route("/file/view_other/<int:file_id>/<format>", methods=["GET"])
def view_file_other_formats(file_id, format):
    """
    View files in formats other than UVL: glencoe, dimacs, splot.
    """
    file = HubfileService().get_or_404(file_id)
    filename = file.name

    # Definir el directorio de acuerdo con la estructura de almacenamiento
    directory_path = f"uploads/user_{file.feature_model.data_set.user_id}/dataset_{file.feature_model.data_set_id}/"
    parent_directory_path = os.path.dirname(current_app.root_path)
    file_path = os.path.join(parent_directory_path, directory_path, filename)

    # Validar el tipo de formato solicitado
    if format not in ["glencoe", "cnf", "splot"]:
        return jsonify({"success": False, "error": "Formato no soportado"}), 400

    # Tratar de abrir y leer el archivo del formato adecuado
    try:
        if os.path.exists(file_path):
            # Leer archivo UVL
            with open(file_path, "r") as f:
                content = f.read()

            # Llamar a la función de conversión dependiendo del formato solicitado
            if format == "glencoe":
                content = convert_to_glencoe(content, file)
            elif format == "cnf":
                content = convert_to_dimacs(content, file)
            elif format == "splot":
                content = convert_to_splot(content, file)

            user_cookie = request.cookies.get("view_cookie")
            if not user_cookie:
                user_cookie = str(uuid.uuid4())

            # Verificar si ya existe un registro de vista para este archivo y cookie
            existing_record = HubfileViewRecord.query.filter_by(
                user_id=current_user.id if current_user.is_authenticated else None,
                file_id=file_id,
                view_cookie=user_cookie,
            ).first()

            if not existing_record:
                # Registrar la visualización del archivo
                new_view_record = HubfileViewRecord(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    file_id=file_id,
                    view_date=datetime.now(),
                    view_cookie=user_cookie,
                )
                db.session.add(new_view_record)
                db.session.commit()

            # Preparar la respuesta con el contenido transformado
            response = jsonify({"success": True, "content": content})
            if not request.cookies.get("view_cookie"):
                response = make_response(response)
                response.set_cookie(
                    "view_cookie", user_cookie, max_age=60 * 60 * 24 * 365 * 2
                )

            return response
        else:
            return jsonify({"success": False, "error": "File not found"}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hubfile_bp.route('/file/edit/<int:file_id>', methods=['POST'])
def edit_file(file_id):
    file = HubfileService().get_or_404(file_id)
    filename = file.name
    directory_path = f"uploads/user_{file.feature_model.data_set.user_id}/dataset_{file.feature_model.data_set_id}/"
    parent_directory_path = os.path.dirname(current_app.root_path)
    file_path = os.path.join(parent_directory_path, directory_path, filename)
    # Get conent from request
    content = request.json.get('content')
    # Check if the user is the owner of the file
    try:
        if os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)
            user_cookie = request.cookies.get('view_cookie')
            if not user_cookie:
                user_cookie = str(uuid.uuid4())
            # Check if the view record already exists for this cookie
            existing_record = HubfileViewRecord.query.filter_by(
                user_id=current_user.id if current_user.is_authenticated else None,
                file_id=file_id,
                view_cookie=user_cookie
            ).first()
            if not existing_record:
                # Register file view
                new_view_record = HubfileViewRecord(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    file_id=file_id,
                    view_date=datetime.now(),
                    view_cookie=user_cookie
                )
                db.session.add(new_view_record)
                db.session.commit()
            # Prepare response
            response = jsonify({'success': True, 'content': content})
            if not request.cookies.get('view_cookie'):
                response = make_response(response)
                response.set_cookie('view_cookie', user_cookie, max_age=60*60*24*365*2)
            return response
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def convert_to_glencoe(content, file):
    # Implementación para convertir el contenido a formato Glencoe
    temp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    fm = UVLReader(file.get_path()).transform()
    GlencoeWriter(temp_file.name, fm).transform()
    with open(temp_file.name, "r") as f:
        glencoe_content = f.read()
    os.remove(temp_file.name)
    return glencoe_content


def convert_to_dimacs(content, file):
    # Implementación para convertir el contenido a formato Dimacs
    temp_file = tempfile.NamedTemporaryFile(suffix=".cnf", delete=False)
    fm = UVLReader(file.get_path()).transform()
    sat = FmToPysat(fm).transform()
    DimacsWriter(temp_file.name, sat).transform()
    with open(temp_file.name, "r") as f:
        dimacs_content = f.read()
    os.remove(temp_file.name)
    return dimacs_content


def convert_to_splot(content, file):
    # Implementación para convertir el contenido a formato SPLOT
    temp_file = tempfile.NamedTemporaryFile(suffix=".splx", delete=False)
    fm = UVLReader(file.get_path()).transform()
    SPLOTWriter(temp_file.name, fm).transform()
    with open(temp_file.name, "r") as f:
        splot_content = f.read()
    os.remove(temp_file.name)
    return splot_content

