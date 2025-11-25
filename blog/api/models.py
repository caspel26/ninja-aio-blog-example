import uuid

from ninja_aio.models import ModelSerializer
from django.db import models


class Base(ModelSerializer):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    class ReadSerialzer:
        fields = ['id', 'created_at', 'updated_at']


class Author(Base):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class ReadSerializer:
        fields = Base.ReadSerialzer.fields + [
            'username',
            'email',
        ]
        customs = [('full_name', str, '')]

    def __str__(self):
        return f"{self.username}@{self.email}"