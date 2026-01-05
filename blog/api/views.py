from uuid import UUID
from ninja_aio import NinjaAIO
from ninja_aio.views import APIViewSet, APIView, mixins
from ninja_aio.schemas import (
    M2MRelationSchema,
    GenericMessageSchema,
    ObjectsQuerySchema,
)
from ninja.pagination import paginate
from ninja_aio.decorators import unique_view, decorate_view, api_get, api_post
from django.http import HttpRequest

from api import models, schema
from api.auth import AuthorAuth, RefreshAuth

api = NinjaAIO(title="Blog API", version="1.0.0", auth=AuthorAuth())


class AuthorAuthenticatedRequest(HttpRequest):
    author: models.Author


class BaseAuthorRelatedAPI(APIViewSet):
    def views(self):
        @self.router.get(
            "/by-author/{author_id}",
            response={200: list[self.schema_out], 404: GenericMessageSchema},
        )
        @decorate_view(
            unique_view(self),
            paginate(self.pagination_class),
        )
        async def get_by_author(request, author_id: UUID):
            """Retrieve all instances related to a specific author."""
            return await self.model_util.list_read_s(
                self.schema_out,
                request,
                query_data=ObjectsQuerySchema(
                    filters={"author__id": author_id},
                ),
                is_for_read=True,
            )

        @self.api.get(
            f"{self.api_route_path}/by-me",
            response={200: list[self.schema_out], 404: GenericMessageSchema},
            auth=AuthorAuth(),
            tags=[self.router_tag],
        )
        @decorate_view(
            unique_view(self),
            paginate(self.pagination_class),
        )
        async def get_by_me(request: AuthorAuthenticatedRequest):
            """Retrieve all instances related to the authenticated author."""
            return await self.model_util.list_read_s(
                self.schema_out,
                request,
                query_data=ObjectsQuerySchema(
                    filters={"author": request.author},
                ),
                is_for_read=True,
            )


@api.view("/login", tags=["Authentication"])
class LoginAPI(APIView):
    @api_post(
        "",
        response={
            200: schema.LoginSchemaOut,
            404: GenericMessageSchema,
            401: GenericMessageSchema,
        },
    )
    async def login(self, request, data: schema.LoginSchemaIn):
        """Authenticate an author and return JWT tokens."""
        author = await models.Author.authenticate(**data.model_dump())
        access_token, refresh_token = author.create_jwt_tokens()
        return 200, {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @api_post(
        "/refresh",
        response={
            200: schema.RefeshSchemaOut,
            404: GenericMessageSchema,
            401: GenericMessageSchema,
        },
        auth=RefreshAuth(),
    )
    async def refresh_token(self, request: AuthorAuthenticatedRequest):
        """Refresh JWT tokens using a valid refresh token."""
        return 200, {
            "access_token": request.author.create_access_token(),
        }

    @api_post(
        "/change-password",
        response={
            200: GenericMessageSchema,
            404: GenericMessageSchema,
            401: GenericMessageSchema,
        },
    )
    async def change_password(
        self, request: AuthorAuthenticatedRequest, data: schema.ChangePasswordSchemaIn
    ):
        """Change the authenticated author's password."""
        author = request.author
        await author.check_password(data.old_password)
        author.password = data.new_password
        await author.asave()
        return {"message": "Password changed successfully."}


@api.viewset(models.Author)
class AuthorAPI(mixins.IcontainsFilterViewSetMixin):
    post_auth = None  # Allow unauthenticated access to create authors
    disable = ["retrieve"]
    query_params = {
        "username": (str, ""),
        "email": (str, ""),
        "first_name": (str, ""),
        "last_name": (str, ""),
    }

    @api_get(
        "/me",
        response={200: models.Author.generate_read_s(), 400: GenericMessageSchema},
        auth=AuthorAuth(),
    )
    async def get_me(self, request: AuthorAuthenticatedRequest):
        """Retrieve the authenticated author's details."""
        return await self.model_util.read_s(
            self.schema_out,
            request,
            request.author,
        )


@api.viewset(models.Post)
class PostAPI(mixins.IcontainsFilterViewSetMixin, BaseAuthorRelatedAPI):
    m2m_relations = [
        M2MRelationSchema(
            model=models.Tag,
            related_name="tags",
            append_slash=True,
        ),
        M2MRelationSchema(
            model=models.Category,
            related_name="categories",
            append_slash=True,
        ),
    ]
    query_params = {
        "title": (str, ""),
    }


@api.viewset(models.Comment)
class CommentAPI(BaseAuthorRelatedAPI):
    pass


@api.viewset(models.Category)
class CategoryAPI(mixins.IcontainsFilterViewSetMixin):
    query_params = {
        "name": (str, ""),
    }


@api.viewset(models.Tag)
class TagAPI(mixins.IcontainsFilterViewSetMixin):
    model = models.Tag
    query_params = {
        "name": (str, ""),
    }
