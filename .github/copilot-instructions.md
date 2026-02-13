Act as a senior Django engineer and generate a complete `.github/copilot-instructions.md` for this repository.

Repository context:
- Django project already advanced and modular.
- Uses multiple apps (e.g., accounts, dashboard, products, cart, orders, goals).
- Uses Bootstrap 5 templates and often `django-widget-tweaks`.
- Mix of CBVs (CRUD) and FBVs for action endpoints.
- Uses groups/permissions (admin vs user) and protects views accordingly.
- Uses services layer (business logic) and wants views thin.
- Python 3.12, Django 5.x style conventions.

Requirements for the instructions file:
1) Clear rules for code style and architecture:
   - where to put business logic (services.py), query logic (selectors.py optional), validations (forms.py / model clean), permissions.
2) Security rules:
   - CSRF, IDOR prevention (scope by request.user), safe file upload handling, no hardcoded secrets, use settings/env.
3) Performance rules:
   - select_related/prefetch_related, avoid N+1, pagination.
4) Testing rules:
   - recommended test layout, what to test, and naming conventions.
5) Templates/UI rules:
   - Bootstrap 5 patterns, widget_tweaks usage, keep templates dumb, use perms for UI gating.
6) Output conventions for Copilot:
   - Always include file path header comment, minimal imports, type hints, docstrings, and short comments for non-obvious logic.
7) Provide an app folder structure template and naming conventions for urls, views, templates.
8) Include Git conventions:
   - conventional commits (`feat(app):`, `fix(app):`, etc.) and small PRs.

Deliverable:
- Output ONLY the final content of `.github/copilot-instructions.md` in Markdown.
- Do not add extra explanations outside the file.
