# Deploy Billing Management Online

This project is configured for a real online deployment on Render with a real PostgreSQL database.

## What You Will Get

- Live Django website URL
- Live PostgreSQL database
- Automatic dependency installation from `requirements.txt`
- Automatic `collectstatic`
- Automatic database migrations

## Files Required In GitHub

Make sure these files are uploaded:

```text
manage.py
requirements.txt
Procfile
build.sh
render.yaml
.gitignore
billing_management/
accounts/
customers/
dashboard/
expenses/
inventory/
invoices/
products/
reports/
sales/
settings_app/
static/
templates/
```

Do not upload:

```text
.venv/
venv/
.env
db.sqlite3
*.log
staticfiles/
media/
```

## Deploy On Render

1. Push this project to GitHub.
2. Open Render.
3. Click **New**.
4. Click **Blueprint**.
5. Connect your GitHub repository.
6. Render will read `render.yaml`.
7. Render will create:
   - `vyapar-billing` web service
   - `vyapar-billing-db` PostgreSQL database
8. Click **Apply**.

## After First Deployment

Open the Render web service shell and run:

```bash
python manage.py createsuperuser
```

Then open your live website URL and log in with that admin account.

## Important Notes

The online database will be PostgreSQL, not your local `db.sqlite3`.

If you need your local SQLite data online, export it locally and import it after deployment:

```bash
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json
python manage.py loaddata data.json
```

Uploaded media files need persistent storage or cloud storage for production. Render free web services do not permanently keep uploaded media files unless you configure persistent disk or external storage.
