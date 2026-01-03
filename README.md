# Ninja AIO Blog Example

A minimal, production-oriented example demonstrating integration of the django-ninja-aio-crud framework within a Django 6 project. This repository showcases a blog API with JWT (RS256) authentication, including authors, posts, comments, tags, and categories, plus a management command to seed demo data.

Framework repository: https://github.com/caspel26/django-ninja-aio-crud
Docs: https://django-ninja-aio.com

## Project Layout

- Django project: [blog/](blog)
  - Settings: [blog/blog/settings.py](blog/blog/settings.py)
  - URLs: [blog/blog/urls.py](blog/blog/urls.py)
  - WSGI/ASGI: [blog/blog/wsgi.py](blog/blog/wsgi.py), [blog/blog/asgi.py](blog/blog/asgi.py)
- App: [blog/api](blog/api)
  - Models: [blog/api/models.py](blog/api/models.py)
  - Views (API): [blog/api/views.py](blog/api/views.py)
  - Auth (JWT): [blog/api/auth.py](blog/api/auth.py)
  - Schemas: [blog/api/schema.py](blog/api/schema.py)
  - Admin: [blog/api/admin.py](blog/api/admin.py)
  - Management command + seed data: [blog/api/management/commands/load_data.py](blog/api/management/commands/load_data.py), [blog/api/management/data.py](blog/api/management/data.py)
- JWT RSA keys: [blog/jwt_secrets/private.pem](blog/jwt_secrets/private.pem), [blog/jwt_secrets/public.pem](blog/jwt_secrets/public.pem)

## Requirements

See [requirements.txt](requirements.txt). Key packages:

- Django 6.0
- django-ninja 1.5.1
- django-ninja-aio-crud 2.2.0
- joserfc (RSA keys handling)

## Configuration

Core settings live in [`blog.blog.settings`](blog/blog/settings.py):

- JWT keys loaded from [jwt_secrets](blog/jwt_secrets)
- Algorithm: RS256 (`JWT_ALGORITHM`)
- Token durations: `JWT_ACCESS_DURATION`, `JWT_REFRESH_DURATION`
- Audience/issuer: `API_SITE_BASEURL`, `JWT_COMMON_ISSUER`

API root is mounted at `/api/` in [`blog.blog.urls`](blog/blog/urls.py).

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```sh
   python blog/manage.py migrate
   ```
4. Seed demo data (creates an admin user and random content):
   ```sh
   python blog/manage.py load_data
   ```

## Run

```sh
python blog/manage.py runserver
```

Visit:

- Admin: http://localhost:8000/admin/
- API root: http://localhost:8000/api/

## Authentication

JWT Bearer via RS256. Verification is implemented in:

- Access tokens: [`api.auth.AuthorAuth`](blog/api/auth.py)
- Refresh tokens: [`api.auth.RefreshAuth`](blog/api/auth.py)

Authors generate tokens with:

- [`api.models.Author.create_access_token`](blog/api/models.py)
- [`api.models.Author.create_refresh_token`](blog/api/models.py)
- [`api.models.Author.create_jwt_tokens`](blog/api/models.py)

Claims include `sub` (username), `email`, `name`, `iss`, `aud`, and `access` or `refresh`.

## Endpoints

Defined in [`api.views`](blog/api/views.py) using NinjaAIO.

- Auth

  - POST `/api/login/` → [`api.schema.LoginSchemaOut`](blog/api/schema.py)
  - POST `/api/login/refresh/` → [`api.schema.RefeshSchemaOut`](blog/api/schema.py) (requires refresh token)
  - POST `/api/login/change-password/` → change password for the authenticated author

- Authors

  - GET `/api/author/me` → current author details
  - CRUD on `/api/author/` (create is open, retrieve disabled)

- Posts

  - CRUD on `/api/post/` with m2m relations to tags/categories
  - GET `/api/post/by-author/{author_id}`
  - GET `/api/post/by-me` (authenticated)

- Comments

  - CRUD on `/api/comment/`
  - GET `/api/comment/by-author/{author_id}`
  - GET `/api/comment/by-me` (authenticated)

- Tags

  - CRUD on `/api/tag/` (filter by `name`)

- Categories
  - CRUD on `/api/category/` (filter by `name`)

Pagination is enabled via Ninja’s `paginate` decorator where applicable.

## Models

See [`api.models`](blog/api/models.py):

- [`api.models.Author`](blog/api/models.py) (auth, token helpers)
- [`api.models.Post`](blog/api/models.py)
- [`api.models.Comment`](blog/api/models.py)
- [`api.models.Tag`](blog/api/models.py)
- [`api.models.Category`](blog/api/models.py)

Admin registrations are in [`api.admin`](blog/api/admin.py).

## Future Ideas

- Add a functional frontend using Django templates
