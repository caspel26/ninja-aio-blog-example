from ninja_aio import NinjaAIO
from ninja_aio.views import APIViewSet, APIView
from ninja_aio.schemas import M2MRelationSchema, GenericMessageSchema

from api import models, schema
from api.auth import AuthorAuth

api = NinjaAIO(title="Blog API", version="1.0.0", auth=AuthorAuth())


class BaseAPIViewSet(APIViewSet):
    api = api


class LoginAPI(APIView):
    router_tag = "Authentication"
    api_route_path = "/login"
    api = api

    def views(self):
        @self.router.post(
            "/",
            response={
                200: schema.LoginSchemaOut,
                404: GenericMessageSchema,
                401: GenericMessageSchema,
            },
            auth=None,
        )
        async def login(request, data: schema.LoginSchemaIn):
            """Authenticate an author and return JWT tokens."""
            author = await models.Author.authenticate(**data.model_dump())
            access_token, refresh_token = author.create_jwt_tokens()
            return 200, {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }


class AuthorAPI(BaseAPIViewSet):
    model = models.Author
    post_auth = None  # Allow unauthenticated access to create authors
    disable = ["retrieve"]

    def views(self):
        @self.router.get(
            "/me", response={200: self.schema_out, 400: GenericMessageSchema}
        )
        async def get_me(request):
            """Retrieve the authenticated author's details."""
            return await self.model_util.read_s(
                request,
                request.user,
                self.schema_out,
            )


class PostAPI(BaseAPIViewSet):
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


class CommentAPI(BaseAPIViewSet):
    model = models.Comment


class CategoryAPI(BaseAPIViewSet):
    model = models.Category


class TagAPI(BaseAPIViewSet):
    model = models.Tag


AuthorAPI().add_views_to_route()
PostAPI().add_views_to_route()
CommentAPI().add_views_to_route()
CategoryAPI().add_views_to_route()
TagAPI().add_views_to_route()
LoginAPI().add_views_to_route()