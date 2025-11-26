from django.contrib import admin

from api import models


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "created_at")
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at")
    search_fields = ("title", "content", "author__username")


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at")
    search_fields = ("content", "author__username", "post__title")


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    filter_horizontal = ("posts",)


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    filter_horizontal = ("posts",)
