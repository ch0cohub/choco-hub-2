import logging
import os
import json
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from zipfile import ZipFile
from sqlalchemy import or_


from flask import (
    redirect,
    render_template,
    request,
    jsonify,
    send_from_directory,
    make_response,
    abort,
    url_for,
    send_file,
)
from flask_login import login_required, current_user

from app.modules.dataset.forms import DataSetForm
from app.modules.dataset.models import DSDownloadRecord, DataSet, DatasetReview
from app.modules.dataset import dataset_bp
from app.modules.dataset.services import (
    AuthorService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
    DataSetService,
    DOIMappingService,
)
from app.modules.community.models import Community
from app import db
from app.modules.community.services import CommunityService

from app.modules.fakenodo.services import FakeNodoService

logger = logging.getLogger(__name__)


dataset_service = DataSetService()
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()
fakenodo_service = FakeNodoService()
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()
community_service = CommunityService()


@dataset_bp.route("/dataset/upload", methods=["GET", "POST"])
@login_required
def create_dataset():
    form = DataSetForm()
    if request.method == "POST":

        dataset = None

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating dataset...")
            dataset = dataset_service.create_from_form(
                form=form, current_user=current_user
            )
            logger.info(f"Created dataset: {dataset}")
            dataset_service.move_feature_models(dataset)
        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return (
                jsonify({"Exception while create dataset data in local: ": str(exc)}),
                400,
            )

        # Aquí se simula la creación del deposition en FakeNodo
        try:
            # Simula la creación del deposition en FakeNodo
            deposition_data = fakenodo_service.create_new_deposition(
                dataset.ds_meta_data.title, dataset.ds_meta_data.description
            )
            deposition_id = deposition_data.get("id")
            deposition_doi = deposition_data.get("doi")
            logger.info(
                f"Deposition created with ID: {deposition_id} and DOI: {deposition_doi}"
            )

            # Actualiza los metadatos del dataset con el ID y DOI del deposition
            dataset_service.update_dsmetadata(
                dataset.ds_meta_data_id,
                deposition_id=deposition_id,
                dataset_doi=deposition_doi,
            )

        except Exception as exc:
            logger.exception(f"Exception while simulating deposition creation: {exc}")
            return (
                jsonify({"Exception while simulating deposition creation: ": str(exc)}),
                400,
            )

        try:
            zenodo_response_json = fakenodo_service.create_new_deposition(
                dataset, description="Simulating deposition creation on FakeNodo"
            )
            response_data = json.dumps(zenodo_response_json)
            data = json.loads(response_data)
            if data.get("conceptrecid"):
                deposition_id = data.get("id")
                dataset_service.update_dsmetadata(
                    dataset.ds_meta_data_id, deposition_id=deposition_id
                )
                # Realizar otras operaciones como carga de archivos o publicación
        except Exception as exc:
            logger.exception(f"Exception while creating dataset in Zenodo {exc}")

        # Limpieza de archivos temporales
        file_path = current_user.temp_folder()
        if os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)

        msg = "Dataset created and synchronized with FakeNodo!"
        return jsonify({"message": msg}), 200

    return render_template("dataset/upload_dataset.html", form=form)


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():
    owned_communities = list(current_user.owned_communities)
    joined_communities = list(current_user.joined_communities)
    all_communities = owned_communities + joined_communities
    return render_template(
        "dataset/list_datasets.html",
        datasets=dataset_service.get_synchronized(current_user.id),
        local_datasets=dataset_service.get_unsynchronized(current_user.id),
        communities=all_communities,
    )


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["file"]
    temp_folder = current_user.temp_folder()

    if not file or not file.filename.endswith(".uvl"):
        return jsonify({"message": "No valid file"}), 400

    # create temp folder
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    file_path = os.path.join(temp_folder, file.filename)

    if os.path.exists(file_path):
        # Generate unique filename (by recursion)
        base_name, extension = os.path.splitext(file.filename)
        i = 1
        while os.path.exists(
            os.path.join(temp_folder, f"{base_name} ({i}){extension}")
        ):
            i += 1
        new_filename = f"{base_name} ({i}){extension}"
        file_path = os.path.join(temp_folder, new_filename)
    else:
        new_filename = file.filename

    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    return (
        jsonify(
            {
                "message": "UVL uploaded and validated successfully",
                "filename": new_filename,
            }
        ),
        200,
    )


@dataset_bp.route('/api/dataset/like', methods=['POST'])
def like_dataset():
    data = request.get_json()
    dataset_id = data.get('dataset_id')
    user_id = current_user.id
    value = data.get('value')

    if not dataset_id or not user_id or value is None:
        return jsonify({"error": "Invalid data"}), 400

    # Find existing review or create a new one
    review = DatasetReview.query.filter_by(data_set_id=dataset_id, user_id=user_id).first()
    if review:
        review.value = value
    else:
        review = DatasetReview(data_set_id=dataset_id, user_id=user_id, value=value)
        db.session.add(review)

    db.session.commit()

    total_likes = db.session.query(db.func.sum(DatasetReview.value)) \
                        .filter(DatasetReview.data_set_id == dataset_id,
                                or_(DatasetReview.value == 1, DatasetReview.value == -1)) \
                        .scalar() or 0

    return jsonify({"total_likes": total_likes})


@dataset_bp.route("/dataset/file/delete", methods=["POST"])
def delete():
    data = request.get_json()
    filename = data.get("file")
    temp_folder = current_user.temp_folder()
    filepath = os.path.join(temp_folder, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"})

    return jsonify({"error": "Error: File not found"})


@dataset_bp.route("/dataset/download/<int:dataset_id>", methods=["GET"])
def download_dataset(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)
    dataset_title = dataset.ds_meta_data.title

    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"{dataset_title}_uvl.zip")

    with ZipFile(zip_path, "w") as zipf:
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(subdir, file)

                relative_path = os.path.relpath(full_path, file_path)

                zipf.write(
                    full_path,
                    arcname=os.path.join(
                        os.path.basename(zip_path[:-4]), relative_path
                    ),
                )

    user_cookie = request.cookies.get("download_cookie")
    if not user_cookie:
        user_cookie = str(
            uuid.uuid4()
        )  # Generate a new unique identifier if it does not exist
        # Save the cookie to the user's browser
        resp = make_response(
            send_from_directory(
                temp_dir,
                f"{dataset_title}_uvl.zip",
                as_attachment=True,
                mimetype="application/zip",
            )
        )
        resp.set_cookie("download_cookie", user_cookie)
    else:
        resp = send_from_directory(
            temp_dir,
            f"{dataset_title}_uvl.zip",
            as_attachment=True,
            mimetype="application/zip",
        )

    # Check if the download record already exists for this cookie
    existing_record = DSDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        dataset_id=dataset_id,
        download_cookie=user_cookie,
    ).first()

    if not existing_record:
        # Record the download in your database
        DSDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    return resp


@dataset_bp.route("/doi/<path:doi>/", methods=["GET"])
def subdomain_index(doi):

    # Check if the DOI is an old DOI
    new_doi = doi_mapping_service.get_new_doi(doi)
    if new_doi:
        # Redirect to the same path with the new DOI
        return redirect(url_for("dataset.subdomain_index", doi=new_doi), code=302)

    # Try to search the dataset by the provided DOI (which should already be the new one)
    ds_meta_data = dsmetadata_service.filter_by_doi(doi)

    if not ds_meta_data:
        abort(404)

    # Get dataset
    dataset = ds_meta_data.data_set

    # Save the cookie to the user's browser
    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)
    resp = make_response(render_template("dataset/view_dataset.html", dataset=dataset))
    resp.set_cookie("view_cookie", user_cookie)

    return resp


@dataset_bp.route("/dataset/unsynchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_unsynchronized_dataset(dataset_id):

    # Get dataset
    dataset = dataset_service.get_unsynchronized_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)

    return render_template("dataset/view_dataset.html", dataset=dataset)


@dataset_bp.route("/dataset/download/all", methods=["GET"])
def download_all_dataset():

    zip_path, zip_filename = dataset_service.generate_datasets_and_name_zip()
    return send_file(zip_path, as_attachment=True, download_name=zip_filename)


@dataset_bp.route("/dataset/update_community", methods=["POST"])
@login_required
def update_dataset_community():
    data = request.get_json()  # Captura los datos enviados como JSON
    dataset_id = data.get("dataset_id")
    community_id = data.get("community_id")

    if not dataset_id or not community_id:
        return jsonify({"error": "Dataset ID and Community ID are required"}), 400

    dataset = dataset_service.get_or_404(dataset_id)
    community = community_service.get_or_404(community_id)

    if not dataset or not community:
        return jsonify({"error": "Dataset or Community not found"}), 404

    dataset.community_id = community.id
    db.session.commit()

    return jsonify({"message": "Dataset updated successfully"})


@dataset_bp.route("/dataset/remove_community", methods=["POST"])
@login_required
def remove_dataset_community():
    dataset_id = request.json.get("dataset_id")
    community_id = request.json.get("community_id")

    dataset = dataset_service.get_or_404(dataset_id)
    community = community_service.get_or_404(community_id)

    if not dataset or not community:
        return jsonify({"error": "Dataset or Community not found"}), 404

    if dataset.community_id == community.id:
        dataset.community_id = None
        db.session.commit()
        return jsonify({"message": "Community association removed successfully"})

    return jsonify({"error": "Dataset is not associated with the community"}), 400
