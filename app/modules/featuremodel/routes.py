

from flask import jsonify, render_template, request
from app.modules.featuremodel import featuremodel_bp
from app.modules.featuremodel.models import FeatureModelReview
from sqlalchemy import or_
from flask_login import current_user
from app import db


@featuremodel_bp.route("/featuremodel", methods=["GET"])
def index():
    return render_template("featuremodel/index.html")


@featuremodel_bp.route('/api/feature_model/like', methods=['POST'])
def like_feature_model():
    data = request.get_json()
    feature_model_id = data.get('feature_model_id')
    user_id = current_user.id
    print(user_id)
    value = data.get('value')

    if not feature_model_id or not user_id or value is None or (value != 1 and value != -1):
        return jsonify({"error": "Invalid data"}), 400

    # Find existing review or create a new one
    review = FeatureModelReview.query.filter_by(feature_model_id=feature_model_id, user_id=user_id).first()
    if review:
        review.value = value
    else:
        review = FeatureModelReview(feature_model_id=feature_model_id, user_id=user_id, value=value)
        db.session.add(review)

    db.session.commit()

    total_likes = db.session.query(db.func.sum(FeatureModelReview.value)) \
                        .filter(FeatureModelReview.feature_model_id == feature_model_id) \
                        .scalar() or 0
    print(total_likes)

    return jsonify({"total_likes": total_likes})