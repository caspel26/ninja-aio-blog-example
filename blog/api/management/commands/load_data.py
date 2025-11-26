from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ninja_aio.models import ModelSerializer

from api import models
from api.management.data import (
    AUTHORS_DATA,
    POSTS_DATA,
    COMMENTS_DATA,
    TAGS_DATA,
    CATEGORIES_DATA,
)


class Command(BaseCommand):
    help = "Load initial data into the database."
    command_name = "load_data"

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            self._handle(*args, **options)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading data: {e}"))
            transaction.set_rollback(True)
            exit(1)

    def _handle(self, *args, **options):
        try:
            User.objects.create_superuser(
                username="admin",
                password="Password123",
            )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Admin user already exists: {e}"))
        self._create_objects(models.Tag, TAGS_DATA)
        self._create_objects(models.Category, CATEGORIES_DATA)
        self._create_objects(models.Author, AUTHORS_DATA)
        self._create_objects(
            models.Post,
            self._add_relation_to_data(POSTS_DATA, ["author"], [models.Author]),
            m2m_relations=[("tags", models.Tag), ("categories", models.Category)],
        )
        self._create_objects(
            models.Comment,
            self._add_relation_to_data(
                COMMENTS_DATA, ["author", "post"], [models.Author, models.Post]
            ),
        )
        self.stdout.write(self.style.SUCCESS("Initial data loaded successfully."))

    def _get_random_object(self, model):
        return model.objects.order_by("?").first()

    def _add_relation_to_data(
        self,
        data: list[dict],
        relation_names: list[str],
        related_objs: list[ModelSerializer],
    ):
        for d in data:
            for relation_name, related_obj in zip(relation_names, related_objs):
                d[relation_name] = self._get_random_object(related_obj)
        return data

    def _create_objects(
        self,
        model: ModelSerializer,
        data_list: list[dict],
        m2m_relations: list[tuple[str, ModelSerializer]] = None,
    ):
        objs = []
        for data in data_list:
            obj, created = model.objects.get_or_create(**data)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created {model.__name__}: {obj}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"{model.__name__} already exists: {obj}")
                )
            if m2m_relations is not None:
                for relation in m2m_relations:
                    getattr(obj, relation[0]).add(self._get_random_object(relation[1]))
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Added M2M relation {relation[0]} for {model.__name__}: {obj}"
                        )
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Added M2M relations for {model.__name__}: {obj}"
                    )
                )
            objs.append(obj)
        return objs
