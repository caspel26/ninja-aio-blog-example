from uuid import UUID
from ninja_aio import NinjaAIO
from ninja_aio.views import APIViewSet, APIView
from ninja_aio.schemas import M2MRelationSchema, GenericMessageSchema
from ninja_aio.decorators import unique_view

from api import models, schema
from api.auth import AuthorAuth, RefreshAuth

api = NinjaAIO(title="Blog API", version="1.0.0", auth=AuthorAuth())


class BaseAPIViewSet(APIViewSet):
    api = api


class BaseIcontainsFilterAPI(BaseAPIViewSet):
    async def query_params_handler(self, queryset, filters):
        """
        Apply icontains filter to the queryset based on provided filters.
        """
        return queryset.filter(
            **{
                f"{key}__icontains": value
                for key, value in filters.items()
                if isinstance(value, str)
            }
        )


class BaseAuthorRelatedAPI(BaseAPIViewSet):
    def views(self):
        @self.router.get(
            "/by-author/{author_id}",
            response={200: list[self.schema_out], 404: GenericMessageSchema},
        )
        @unique_view(self)
        async def get_by_author(request, author_id: UUID):
            """Retrieve all instances related to a specific author."""
            queryset = await self.model_util.get_object(
                request,
                filters={"author__id": author_id},
            )
            return [
                await self.model_util.read_s(request, obj, self.schema_out)
                async for obj in queryset
            ]

        @self.api.get(
            f"{self.api_route_path}/by-me",
            response={200: list[self.schema_out], 404: GenericMessageSchema},
            auth=AuthorAuth(),
            tags=[self.router_tag],
        )
        @unique_view(self)
        async def get_by_me(request):
            """Retrieve all instances related to the authenticated author."""
            queryset = await self.model_util.get_object(
                request,
                filters={"author": request.user},
            )
            return [
                await self.model_util.read_s(request, obj, self.schema_out)
                async for obj in queryset
            ]


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

        @self.router.post(
            "/refresh/",
            response={
                200: schema.RefeshSchemaOut,
                404: GenericMessageSchema,
                401: GenericMessageSchema,
            },
            auth=RefreshAuth(),
        )
        async def refresh_token(request):
            """Refresh JWT tokens using a valid refresh token."""
            author = request.user
            return 200, {
                "access_token": author.create_access_token(),
            }

        @self.router.post(
            "/change-password/",
            response={200: GenericMessageSchema, 404: GenericMessageSchema, 401: GenericMessageSchema},
        )
        async def change_password(request, data: schema.ChangePasswordSchemaIn):
            """Change the authenticated author's password."""
            author = request.user
            await author.check_password(data.old_password)
            author.password = data.new_password
            await author.asave()
            return {"message": "Password changed successfully."}


class AuthorAPI(BaseIcontainsFilterAPI):
    model = models.Author
    post_auth = None  # Allow unauthenticated access to create authors
    disable = ["retrieve"]
    query_params = {
        "username": (str, ""),
        "email": (str, ""),
        "first_name": (str, ""),
        "last_name": (str, ""),
    }

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


class PostAPI(BaseAuthorRelatedAPI, BaseIcontainsFilterAPI):
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
    query_params = {
        "title": (str, ""),
    }


class CommentAPI(BaseAuthorRelatedAPI):
    model = models.Comment


class CategoryAPI(BaseIcontainsFilterAPI):
    model = models.Category
    query_params = {
        "name": (str, ""),
    }


class TagAPI(BaseIcontainsFilterAPI):
    model = models.Tag
    query_params = {
        "name": (str, ""),
    }


AuthorAPI().add_views_to_route()
PostAPI().add_views_to_route()
CommentAPI().add_views_to_route()
CategoryAPI().add_views_to_route()
TagAPI().add_views_to_route()
LoginAPI().add_views_to_route()
