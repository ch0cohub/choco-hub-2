from flask import jsonify, send_file, request
from . import fakenodo_bp
import tempfile
import os

datasets = {}
dataset_counter = 0


@fakenodo_bp.route("/fakenodo/datasets", methods=["GET"])
def list_datasets():
    datasets_list = [d for d in datasets.values()]
    return jsonify(datasets_list)


@fakenodo_bp.route("/fakenodo/info/<dataset_id>", methods=["GET"])
def get_dataset(dataset_id):
    dataset = datasets.get(dataset_id)
    if dataset:

        return send_file(
            dataset["file_path"],
            as_attachment=True,
        )
    return jsonify({"error": f"Dataset with ID {dataset_id} not found"}), 404


@fakenodo_bp.route("/fakenodo/upload", methods=["POST"])
def upload_dataset():

    global dataset_counter

    uploaded_file = request.files.get("file")
    if uploaded_file:

        dataset_id = dataset_counter
        dataset_counter += 1

        temporary_directory = tempfile.mkdtemp()
        file_path = os.path.join(temporary_directory, uploaded_file.filename)
        uploaded_file.save(file_path)

        datasets[dataset_id] = {
            "id": dataset_id,
            "filename": uploaded_file.filename,
            "file_path": file_path,
        }
        return jsonify({"id": dataset_id, "filename": uploaded_file.filename}), 201

    return jsonify({"error": "No file was uploaded"}), 400


@fakenodo_bp.route("/fakenodo/dataset/<int:dataset_id>", methods=["DELETE"])
def delete_dataset(dataset_id):

    dataset = datasets.pop(dataset_id, None)
    if dataset:
        os.unlink(dataset["file_path"])
        return jsonify({"message": f"Dataset {dataset_id} deleted successfully"}), 200

    return jsonify({"error": f"Dataset with ID {dataset_id} not found"}), 404
