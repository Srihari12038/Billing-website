# Billing Management System

Vyapar-inspired Django billing and inventory system for Windows/PyCharm.

## Run Locally

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Open `http://127.0.0.1:8000/`.

Local admin login created during setup:

```text
username: admin
password: Admin@12345
```

## MySQL

Copy `.env.example` to `.env`, set `DB_ENGINE=mysql`, then fill `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`. Run migrations again after creating the MySQL database.

## Deploy Online

This project is ready for Render deployment with `render.yaml`.

1. Push the project to GitHub.
2. In Render, choose **New > Blueprint** and select the GitHub repository.
3. Render will create the web service and PostgreSQL database from `render.yaml`.
4. After the first deploy, open the Render shell and create an admin user:

```bash
python manage.py createsuperuser
```

For another host, use:

```bash
python manage.py collectstatic --no-input
python manage.py migrate --no-input
gunicorn billing_management.wsgi:application
```

Required production environment variables:

```text
DEBUG=0
SECRET_KEY=<long-random-secret>
ALLOWED_HOSTS=<your-domain>
CSRF_TRUSTED_ORIGINS=https://<your-domain>
DATABASE_URL=<postgres-or-other-database-url>
```

User-uploaded media files are stored on the server filesystem by default. For permanent uploaded logos/documents on hosts with ephemeral disks, configure persistent disk storage or cloud media storage.

## WhatsApp

If `WHATSAPP_CLOUD_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID` are configured, invoice sharing uploads the generated PDF to WhatsApp Business Cloud API and sends it as a document. Without those values, the app opens WhatsApp Web with a pre-filled invoice message.
