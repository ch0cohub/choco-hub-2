import re
from app import db
from sqlalchemy import any_, func, or_
import unidecode
from app.modules.dataset.models import (
    Author,
    DSMetaData,
    DataSet,
    PublicationType,
    DSViewRecord,
    DSDownloadRecord,
)
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from core.repositories.BaseRepository import BaseRepository


class ExploreRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def filter(self, search_criteria, **kwargs):
        # we have to check existence of keys in the dictionary because in the tests not all of them will be present
        title = search_criteria.get("title", None)
        publication_type = search_criteria.get("publication_type", None)
        sorting = search_criteria.get("sorting", None)
        uvl_validation = search_criteria.get("uvl_validation", None)
        num_authors = search_criteria.get("num_authors", None)
        tags_str = search_criteria.get("tags_str", None)
        tags = [t.strip() for t in tags_str.split(",")] if tags_str else None
        author_name = search_criteria.get("author_name", None)

        # Normalize and remove unwanted characters
        normalized_title = unidecode.unidecode(title).lower() if title else None
        cleaned_title = (
            re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_title)
            if normalized_title
            else None
        )
        filters = []
        if cleaned_title:
            for word in cleaned_title.split():
                filters.append(DSMetaData.title.ilike(f"%{word}%"))

        datasets = (
            self.model.query.join(DataSet.ds_meta_data)
            .join(DSMetaData.authors)
            .join(DataSet.feature_models)
            .join(FeatureModel.fm_meta_data)
            .filter(or_(*filters))
            .filter(
                DSMetaData.dataset_doi.isnot(None)
            )  # Exclude datasets with empty dataset_doi
        )

        if publication_type and publication_type != "any":
            matching_type = None
            for member in PublicationType:
                if member.value.lower() == publication_type:
                    matching_type = member
                    break
            # we can use "is not None" because in python the "None" is a singleton so there only exists one memory reference to it
            if matching_type is not None:
                datasets = datasets.filter(
                    DSMetaData.publication_type == matching_type.name
                )

        if tags:
            tag_filters = []
            for tag in tags:
                tag_filters.append(DSMetaData.tags.ilike(f"%{tag}%"))
                datasets = datasets.filter(or_(*tag_filters))

        # Order by created_at
        if sorting and sorting == "oldest":
            datasets = datasets.order_by(self.model.created_at.asc())
        elif sorting and sorting == "newest":
            datasets = datasets.order_by(self.model.created_at.desc())
        elif sorting == "most views":
            datasets = (
                datasets.outerjoin(
                    DSViewRecord, DSViewRecord.dataset_id == self.model.id
                )  # Relación con DSViewRecord
                .group_by(self.model.id)  # Agrupar por dataset
                .order_by((db.func.count(DSViewRecord.id)).desc())  # Ordenar por vistas
            )
        elif sorting == "most downloads":
            datasets = (
                datasets.outerjoin(
                    DSDownloadRecord, DSDownloadRecord.dataset_id == self.model.id
                )  # Relación con DSDownloadRecord
                .group_by(self.model.id)  # Agrupar por dataset
                .order_by(
                    (db.func.count(DSDownloadRecord.id)).desc()
                )  # Ordenar por descargas
            )

        # Comprobar si todos los feature models de un dataset tienen uvl_valid = True
        if uvl_validation:
            datasets = datasets.filter(
                ~DataSet.feature_models.any(FeatureModel.uvl_valid == False)
            )

        if num_authors != "any":
            author_count_subquery = (
                db.session.query(
                    DSMetaData.id, func.count(Author.id).label("author_count")
                )
                .join(DSMetaData.authors)
                .group_by(DSMetaData.id)
                .subquery()
            )

            datasets = datasets.join(
                author_count_subquery, author_count_subquery.c.id == DSMetaData.id
            )

            if num_authors == "1":
                datasets = datasets.filter(author_count_subquery.c.author_count == 1)
            elif num_authors == "2-3":
                datasets = datasets.filter(
                    author_count_subquery.c.author_count.between(2, 3)
                )
            elif num_authors == "4+":
                datasets = datasets.filter(author_count_subquery.c.author_count >= 4)

        if author_name:
            datasets = datasets.filter(Author.name.ilike(f"%{author_name}%"))
        return datasets.all()
