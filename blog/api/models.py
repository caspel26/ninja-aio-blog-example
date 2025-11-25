import uuid

from ninja_aio.models import ModelSerializer
from django.db import models
from django.contrib.auth.hashers import make_password


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
    posts: models.QuerySet['Post'] = models.ManyToManyField(
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
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
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