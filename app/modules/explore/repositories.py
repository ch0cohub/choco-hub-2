import re
from sqlalchemy import any_, or_
import unidecode
from app.modules.dataset.models import Author, DSMetaData, DataSet, PublicationType
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from core.repositories.BaseRepository import BaseRepository


class ExploreRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def filter(self, search_criteria, **kwargs):
        print("search criteria desde repository", search_criteria)
        title = search_criteria.get('title', None)
        publication_type = search_criteria.get('publication_type', None)
        sorting = search_criteria.get('sorting', None)
        tags_str = search_criteria.get('tags_str', None)
        tags = [t.strip() for t in tags_str.split(",")] if tags_str else None
        author_name = search_criteria.get('author_name', None)

        # Normalize and remove unwanted characters
        normalized_title = unidecode.unidecode(title).lower() if title else None
        cleaned_title = re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_title) if normalized_title else None
        print("cleaned_title", cleaned_title)
        filters = []
        if cleaned_title:
            for word in cleaned_title.split():
                print("word:", word)
                filters.append(DSMetaData.title.ilike(f"%{word}%"))
                print("filter:", str(DSMetaData.title.ilike(f"%{word}%")))

        print("filters: ", [str(f) for f in filters])

        datasets = (
            self.model.query
            .join(DataSet.ds_meta_data)
            .join(DSMetaData.authors)
            .join(DataSet.feature_models)
            .join(FeatureModel.fm_meta_data)
            .filter(or_(*filters))
            .filter(DSMetaData.dataset_doi.isnot(None))  # Exclude datasets with empty dataset_doi
        )

        print("datasets: ", datasets.all())

        if publication_type and publication_type != "any":
            print("A")
            matching_type = None
            for member in PublicationType:
                if member.value.lower() == publication_type:
                    matching_type = member
                    break

            if matching_type is not None:
                datasets = datasets.filter(DSMetaData.publication_type == matching_type.name)

        if tags:
            print("B")
            tag_filters = []
            for tag in tags:
                tag_filters.append(DSMetaData.tags.ilike(f"%{tag}%"))
                datasets = datasets.filter(or_(*tag_filters))

        # Order by created_at
        if sorting and sorting == "oldest":
            print("C")
            datasets = datasets.order_by(self.model.created_at.asc())
        elif sorting:
            print("D")
            datasets = datasets.order_by(self.model.created_at.desc())

        if author_name:
            print("E")
            datasets = datasets.filter(Author.name.ilike(f"%{author_name}%"))
        return datasets.all()
