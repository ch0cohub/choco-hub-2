import logging
from app import db
from app.modules.hubfile.services import HubfileService
from flask import send_file, jsonify, after_this_request
from app.modules.flamapy import flamapy_bp
from flamapy.metamodels.fm_metamodel.transformations import (
    UVLReader,
    GlencoeWriter,
    SPLOTWriter,
)
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat, DimacsWriter
import tempfile
import os
import zipfile

from antlr4 import CommonTokenStream, FileStream
from uvl.UVLCustomLexer import UVLCustomLexer
from uvl.UVLPythonParser import UVLPythonParser
from antlr4.error.ErrorListener import ErrorListener

from app.modules.dataset.services import DataSetService

logger = logging.getLogger(__name__)

dataset_service = DataSetService()


@flamapy_bp.route("/flamapy/check_uvl/<int:file_id>", methods=["GET"])
def check_uvl(file_id):
    class CustomErrorListener(ErrorListener):
        def __init__(self):
            self.errors = []

        def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
            if "\\t" in msg:
                warning_message = (
                    f"The UVL has the following warning that prevents reading it: "
                    f"Line {line}:{column} - {msg}"
                )
                print(warning_message)
                self.errors.append(warning_message)
            else:
                error_message = (
                    f"The UVL has the following error that prevents reading it: "
                    f"Line {line}:{column} - {msg}"
                )
                self.errors.append(error_message)

    try:
        hubfile = HubfileService().get_by_id(file_id)
        input_stream = FileStream(hubfile.get_path())
        lexer = UVLCustomLexer(input_stream)

        error_listener = CustomErrorListener()

        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        stream = CommonTokenStream(lexer)
        parser = UVLPythonParser(stream)

        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        # tree = parser.featureModel()

        if error_listener.errors:
            feature_model = hubfile.feature_model
            feature_model.uvl_valid = False
            db.session.commit()
            return jsonify({"errors": error_listener.errors}), 400

        feature_model = hubfile.feature_model
        feature_model.uvl_valid = True
        db.session.commit()

        # Optional: Print the parse tree
        # print(tree.toStringTree(recog=parser))

        return jsonify({"message": "Valid Model"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@flamapy_bp.route("/flamapy/valid/<int:file_id>", methods=["GET"])
def valid(file_id):
    return jsonify({"success": True, "file_id": file_id})


@flamapy_bp.route("/flamapy/to_glencoe/<int:file_id>", methods=["GET"])
def to_glencoe(file_id):
    temp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    try:
        hubfile = HubfileService().get_or_404(file_id)
        fm = UVLReader(hubfile.get_path()).transform()
        GlencoeWriter(temp_file.name, fm).transform()

        # Return the file in the response
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f"{hubfile.name}_glencoe.json",
        )
    finally:
        # Clean up the temporary file
        os.remove(temp_file.name)


@flamapy_bp.route("/flamapy/to_splot/<int:file_id>", methods=["GET"])
def to_splot(file_id):
    temp_file = tempfile.NamedTemporaryFile(suffix=".splx", delete=False)
    try:
        hubfile = HubfileService().get_by_id(file_id)
        fm = UVLReader(hubfile.get_path()).transform()
        SPLOTWriter(temp_file.name, fm).transform()

        # Return the file in the response
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f"{hubfile.name}_splot.splx",
        )
    finally:
        # Clean up the temporary file
        os.remove(temp_file.name)


@flamapy_bp.route("/flamapy/to_cnf/<int:file_id>", methods=["GET"])
def to_cnf(file_id):
    temp_file = tempfile.NamedTemporaryFile(suffix=".cnf", delete=False)
    try:
        hubfile = HubfileService().get_by_id(file_id)
        fm = UVLReader(hubfile.get_path()).transform()
        sat = FmToPysat(fm).transform()
        DimacsWriter(temp_file.name, sat).transform()

        # Return the file in the response
        return send_file(
            temp_file.name, as_attachment=True, download_name=f"{hubfile.name}_cnf.cnf"
        )
    finally:
        # Clean up the temporary file
        os.remove(temp_file.name)


@flamapy_bp.route("/flamapy/download/GLENCOE/<int:dataset_id>", methods=["GET"])
def download_glencoe_dataset(dataset_id):
    # Obtener el dataset o devolver un error 404
    dataset = dataset_service.get_or_404(dataset_id)
    dataset_title = dataset.ds_meta_data.title

    # Ruta a los archivos UVL dentro del dataset
    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    # Crear un directorio temporal para almacenar el archivo ZIP
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"{dataset_title}_glencoe.zip")

    # Crear la carpeta dentro del ZIP con el mismo nombre que el archivo ZIP (sin la extensión .zip)
    folder_name = f"{dataset_title}_glencoe"

    @after_this_request
    def cleanup(response):
        try:
            os.remove(zip_path)
            os.rmdir(temp_dir)
        except Exception as e:
            # Podrías querer registrar el error si la limpieza falla
            print(f"Error al limpiar archivos temporales: {e}")
        return response

    # Crear el archivo ZIP
    with zipfile.ZipFile(zip_path, "w") as zipf:
        # Buscar todos los archivos UVL en el directorio del dataset
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                if file.endswith(".uvl"):  # Filtrar solo archivos UVL
                    full_path = os.path.join(subdir, file)

                    # Crear un archivo temporal para el archivo convertido
                    temp_file = tempfile.NamedTemporaryFile(
                        suffix=".json", delete=False
                    )
                    try:
                        # Convertir el archivo UVL a formato Glencoe
                        fm = UVLReader(full_path).transform()
                        GlencoeWriter(temp_file.name, fm).transform()

                        # Crear la ruta relativa dentro de la carpeta en el ZIP
                        relative_path = os.path.relpath(full_path, file_path)
                        file_in_zip = os.path.join(
                            folder_name,
                            f"{relative_path.replace('.uvl', '')}_glencoe.json",
                        )

                        # Agregar el archivo convertido al ZIP dentro de la carpeta
                        zipf.write(temp_file.name, arcname=file_in_zip)
                    finally:
                        # Eliminar el archivo JSON temporal
                        os.remove(temp_file.name)

        # Enviar el archivo ZIP en la respuesta
    return send_file(
        zip_path, as_attachment=True, download_name=f"{dataset_title}_glencoe.zip"
    )


@flamapy_bp.route("/flamapy/download/DIMACS/<int:dataset_id>", methods=["GET"])
def download_dimacs_dataset(dataset_id):
    # Obtener el dataset o devolver un error 404
    dataset = dataset_service.get_or_404(dataset_id)
    dataset_title = dataset.ds_meta_data.title

    # Ruta a los archivos UVL dentro del dataset
    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    # Crear un directorio temporal para almacenar el archivo ZIP
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"{dataset_title}_dimacs.zip")

    # Crear la carpeta dentro del ZIP con el mismo nombre que el archivo ZIP (sin la extensión .zip)
    folder_name = f"{dataset_title}_dimacs"

    @after_this_request
    def cleanup(response):
        try:
            os.remove(zip_path)
            os.rmdir(temp_dir)
        except Exception as e:
            # Podrías querer registrar el error si la limpieza falla
            print(f"Error al limpiar archivos temporales: {e}")
        return response

    # Crear el archivo ZIP
    with zipfile.ZipFile(zip_path, "w") as zipf:
        # Buscar todos los archivos UVL en el directorio del dataset
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                if file.endswith(".uvl"):  # Filtrar solo archivos UVL
                    full_path = os.path.join(subdir, file)

                    # Crear un archivo temporal para el archivo convertido
                    temp_file = tempfile.NamedTemporaryFile(suffix=".cnf", delete=False)
                    try:
                        # Convertir el archivo UVL a formato DIMACS
                        fm = UVLReader(full_path).transform()
                        sat = FmToPysat(fm).transform()
                        DimacsWriter(temp_file.name, sat).transform()

                        # Crear la ruta relativa dentro de la carpeta en el ZIP
                        relative_path = os.path.relpath(full_path, file_path)
                        file_in_zip = os.path.join(
                            folder_name,
                            f"{relative_path.replace('.uvl', '')}_dimacs.cnf",
                        )

                        # Agregar el archivo convertido al ZIP dentro de la carpeta
                        zipf.write(temp_file.name, arcname=file_in_zip)
                    finally:
                        # Eliminar el archivo CNF temporal
                        os.remove(temp_file.name)

    # Enviar el archivo ZIP en la respuesta
    return send_file(
        zip_path, as_attachment=True, download_name=f"{dataset_title}_dimacs.zip"
    )


@flamapy_bp.route("/flamapy/download/SPLOT/<int:dataset_id>", methods=["GET"])
def download_splot_dataset(dataset_id):
    # Obtener el dataset o devolver un error 404
    dataset = dataset_service.get_or_404(dataset_id)
    dataset_title = dataset.ds_meta_data.title

    # Ruta a los archivos UVL dentro del dataset
    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    # Crear un directorio temporal para almacenar el archivo ZIP
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"{dataset_title}_splot.zip")

    # Crear la carpeta dentro del ZIP con el mismo nombre que el archivo ZIP (sin la extensión .zip)
    folder_name = f"{dataset_title}_splot"

    @after_this_request
    def cleanup(response):
        try:
            os.remove(zip_path)
            os.rmdir(temp_dir)
        except Exception as e:
            # Podrías querer registrar el error si la limpieza falla
            print(f"Error al limpiar archivos temporales: {e}")
        return response

    # Crear el archivo ZIP
    with zipfile.ZipFile(zip_path, "w") as zipf:
        # Buscar todos los archivos UVL en el directorio del dataset
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                if file.endswith(".uvl"):  # Filtrar solo archivos UVL
                    full_path = os.path.join(subdir, file)

                    # Crear un archivo temporal para el archivo convertido
                    temp_file = tempfile.NamedTemporaryFile(
                        suffix=".splx", delete=False
                    )
                    try:
                        # Convertir el archivo UVL a formato SPLOT
                        fm = UVLReader(full_path).transform()
                        SPLOTWriter(temp_file.name, fm).transform()

                        # Crear la ruta relativa dentro de la carpeta en el ZIP
                        relative_path = os.path.relpath(full_path, file_path)
                        file_in_zip = os.path.join(
                            folder_name,
                            f"{relative_path.replace('.uvl', '')}_splot.splx",
                        )

                        # Agregar el archivo convertido al ZIP dentro de la carpeta
                        zipf.write(temp_file.name, arcname=file_in_zip)
                    finally:
                        # Eliminar el archivo splx temporal
                        os.remove(temp_file.name)

        # Enviar el archivo ZIP en la respuesta
    return send_file(
        zip_path, as_attachment=True, download_name=f"{dataset_title}_splot.zip"
    )
