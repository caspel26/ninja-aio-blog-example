import uuid

from ninja_aio.models import ModelSerializer
from ninja_aio.exceptions import NotFoundError, AuthError
from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password, acheck_password

from utils.security import encode_jwt


class Base(ModelSerializer):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    class ReadSerialzer:
        fields = ["id", "created_at", "updated_at"]


class BaseAuthorRelated(Base):
    author = models.ForeignKey(
        "Author", on_delete=models.CASCADE, related_name="%(class)ss"
    )

    class Meta:
        abstract = True

    class ReadSerializer:
        fields = Base.ReadSerialzer.fields + [
            "author",
        ]

    class CreateSerializer:
        fields = [
            "author",
        ]


class BasePostRelated(Base):
    posts: models.QuerySet["Post"] = models.ManyToManyField(
        "Post", related_name="%(class)ss"
    )

    class Meta:
        abstract = True


class Author(Base):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class ReadSerializer:
        fields = Base.ReadSerialzer.fields + [
            "username",
            "email",
        ]
        customs = [("full_name", str, "")]

    class CreateSerializer:
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
        ]

    class UpdateSerializer:
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
        ]

    @classmethod
    async def authenticate(cls, username: str, password: str):
        try:
            author = await cls.objects.aget(username=username)
            if not acheck_password(password, author.password):
                raise AuthError("Invalid credentials")
        except cls.DoesNotExist:
            raise NotFoundError(cls)
        return author

    async def check_password(self, password: str) -> bool:
        if not acheck_password(password, self.password):
            raise AuthError("Invalid credentials")
        return True

    def _additional_jwt_claims(self) -> dict:
        return {
            "sub": self.username,
            "email": self.email,
            "name": self.full_name,
        }

    def create_access_token(self) -> str:
        return encode_jwt(
            duration=settings.JWT_ACCESS_DURATION,
            token_type="access",
            **self._additional_jwt_claims(),
        )

    def create_refresh_token(self) -> str:
        return encode_jwt(
            duration=settings.JWT_REFRESH_DURATION,
            token_type="refresh",
            **self._additional_jwt_claims(),
        )

    def create_jwt_tokens(self) -> tuple[str, str]:
        return self.create_access_token(), self.create_refresh_token()

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}@{self.email}"


class Post(BaseAuthorRelated):
    title = models.CharField(max_length=200)
    content = models.TextField()

    class ReadSerializer:
        fields = BaseAuthorRelated.ReadSerializer.fields + [
            "title",
            "content",
        ]

    class CreateSerializer:
        fields = BaseAuthorRelated.CreateSerializer.fields + [
            "title",
            "content",
        ]

    def __str__(self):
        return f"{self.title} by {self.author.username}"


class Comment(BaseAuthorRelated):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()

    class ReadSerializer:
        fields = BaseAuthorRelated.ReadSerializer.fields + [
            "post",
            "content",
        ]

    class CreateSerializer:
        fields = BaseAuthorRelated.CreateSerializer.fields + [
            "post",
            "content",
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Tag(BasePostRelated):
    name = models.CharField(max_length=50, unique=True)

    class ReadSerializer:
        fields = Base.ReadSerialzer.fields + [
            "name",
        ]

    class CreateSerializer:
        fields = [
            "name",
        ]

    def __str__(self):
        return self.name


class Category(BasePostRelated):
    name = models.CharField(max_length=50, unique=True)

    class ReadSerializer:
        fields = Base.ReadSerialzer.fields + [
            "name",
        ]

    class CreateSerializer:
        fields = [
            "name",
        ]

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
