from ninja_aio import NinjaAIO
from ninja_aio.views import APIViewSet
from ninja_aio.schemas import M2MRelationSchema

from api import models
from api.auth import AuthorAuth

api = NinjaAIO(title="Blog API", version="1.0.0", auth=AuthorAuth())


class BaseAPIViewSet(APIViewSet):
    api = api


class AuthorViewSet(BaseAPIViewSet):
    model = models.Author
    post_auth = None  # Allow unauthenticated access to create authors


class PostViewSet(BaseAPIViewSet):
    model = models.Post
    m2m_relations = [
        M2MRelationSchema(
            model=models.Tag,
            related_name="tags",
        ),
        M2MRelationSchema(
            model=models.Category,
            related_name="categories",
        ),
    ]


class CommentViewSet(BaseAPIViewSet):
    model = models.Comment


class CategoryViewSet(BaseAPIViewSet):
    model = models.Category


class TagViewSet(BaseAPIViewSet):
    model = models.Tag


AuthorViewSet().add_views_to_route()
PostViewSet().add_views_to_route()
CommentViewSet().add_views_to_route()
CategoryViewSet().add_views_to_route()
TagViewSet().add_views_to_route()
