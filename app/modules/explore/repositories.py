import re
from app import db
from sqlalchemy import any_, or_
import unidecode
from app.modules.dataset.models import Author, DSMetaData, DataSet, PublicationType, DSViewRecord, DSDownloadRecord
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from core.repositories.BaseRepository import BaseRepository

class ExploreRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def filter(self, query="", sorting="newest", publication_type="any", tags=[], **kwargs):
        # Normalize and remove unwanted characters
        normalized_query = unidecode.unidecode(query).lower()
        cleaned_query = re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_query)

        filters = []
        for word in cleaned_query.split():
            filters.append(DSMetaData.title.ilike(f"%{word}%"))
            filters.append(DSMetaData.description.ilike(f"%{word}%"))
            filters.append(Author.name.ilike(f"%{word}%"))
            filters.append(Author.affiliation.ilike(f"%{word}%"))
            filters.append(Author.orcid.ilike(f"%{word}%"))
            filters.append(FMMetaData.uvl_filename.ilike(f"%{word}%"))
            filters.append(FMMetaData.title.ilike(f"%{word}%"))
            filters.append(FMMetaData.description.ilike(f"%{word}%"))
            filters.append(FMMetaData.publication_doi.ilike(f"%{word}%"))
            filters.append(FMMetaData.tags.ilike(f"%{word}%"))
            filters.append(DSMetaData.tags.ilike(f"%{word}%"))

        datasets = (
            self.model.query
            .join(DataSet.ds_meta_data)
            .join(DSMetaData.authors)
            .join(DataSet.feature_models)
            .join(FeatureModel.fm_meta_data)
            .filter(or_(*filters))
            .filter(DSMetaData.dataset_doi.isnot(None))  # Exclude datasets with empty dataset_doi
        )

        if publication_type != "any":
            matching_type = None
            for member in PublicationType:
                if member.value.lower() == publication_type:
                    matching_type = member
                    break

            if matching_type is not None:
                datasets = datasets.filter(DSMetaData.publication_type == matching_type.name)

        if tags:
            datasets = datasets.filter(DSMetaData.tags.ilike(any_(f"%{tag}%" for tag in tags)))

        # Order by:
        if sorting == "oldest":
            datasets = datasets.order_by(self.model.created_at.asc())
        elif sorting == "newest":
            datasets = datasets.order_by(self.model.created_at.desc())
        elif sorting == "most views":
            datasets = (
                datasets
                .outerjoin(DSViewRecord, DSViewRecord.dataset_id == self.model.id)  # Relación con DSViewRecord
                .group_by(self.model.id)  # Agrupar por dataset
                .order_by((db.func.count(DSViewRecord.id)).desc())  # Ordenar por vistas
            )
        elif sorting == "most downloads":
            datasets = (
                datasets
                .outerjoin(DSDownloadRecord, DSDownloadRecord.dataset_id == self.model.id)  # Relación con DSDownloadRecord
                .group_by(self.model.id)  # Agrupar por dataset
                .order_by((db.func.count(DSDownloadRecord.id)).desc())  # Ordenar por descargas
            )

        return datasets.all()
