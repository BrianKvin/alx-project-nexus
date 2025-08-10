
---

## ✅ Common Ways to Create a PostgreSQL Database

### **1. Using the `psql` shell  ✅**

```bash
sudo -u postgres psql
CREATE DATABASE job_board_db;
```

This is the most direct and universal method.

---

### **2. Using `createdb` command (simpler shell alternative)**

If you want to create a DB without entering `psql`, just run:

```bash
sudo -u postgres createdb job_board_db
```

Or, as a specific user:

```bash
createdb -U postgres -h localhost job_board_db
```

> 🔐 You’ll be prompted for a password if required.

---

### **3. Using a GUI like pgAdmin**

* Install [pgAdmin](https://www.pgadmin.org/)
* Connect to your local server
* Right-click **Databases > Create > Database**
* Name it `job_board_db`, assign an owner, click **Save**

✅ Great for beginners and visual learners

---

### **4. With Docker (for containerized environments)**

In `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: job_board_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: admin123
```

When Docker starts the container, it creates the DB for you.

---

### **5. Using Python or Django directly (Not recommended for real apps)**

You could technically use Django signals or custom scripts to create a DB if it doesn't exist, but:

* It’s **non-standard**
* Adds **complexity**
* Usually better to manage infrastructure outside app logic

---

## ✅ Recommendation

For development:
🔸 Use `psql` or `createdb` command

For production:
🔸 Use infrastructure-as-code (Docker, Ansible, Terraform, etc.) or managed services (like AWS RDS)

For comfort:
🔸 Use pgAdmin if you prefer GUI tools

- For config/setting/ like design, tell django which setting to use
- export DJANGO_SETTINGS_MODULE=config.settings.development

- Alter postgres user and passord
- sudo -u postgres psql
- [sudo] password for bk:         
- psql (16.9 (Ubuntu 16.9-0ubuntu0.24.04.1))
- Type "help" for help.

- postgres=# ALTER USER postgres PASSWORD 'admin123';
- ALTER ROLE
- postgres-# \q
- CREATE DATABASE job_board_db;


- confirm db exist
- sudo -u postgres psql -l

---

# Run server with a specific server
- python3 manage.py runserver --settings=config.settings.base







# Run django in production
Running a Django application in **production** requires several **critical steps** to ensure the app is secure, performant, and stable. Here’s a **complete, detailed, step-by-step guide** for deploying a Django app to production using:

* Gunicorn (WSGI server)
* Nginx (reverse proxy)
* PostgreSQL
* Django settings modularization
* Static files and environment variables
* Optional: SSL (Let's Encrypt)

---

## 🧱 Assumptions

| Component     | Details                          |
| ------------- | -------------------------------- |
| OS            | Ubuntu 20.04+                    |
| App directory | `/home/youruser/yourproject`     |
| Domain        | `yourdomain.com`                 |
| Django module | `config.settings.production`     |
| DB            | PostgreSQL                       |
| Python        | 3.10+                            |
| Virtualenv    | located at `/home/youruser/venv` |

---

## ✅ 1. Create Production Settings File

File: `config/settings/production.py`

```python
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Static files
STATIC_ROOT = BASE_DIR / "staticfiles"

# Logging (optional)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/django.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}
```

---

## ✅ 2. Set Up Environment Variables

Create `.env` in project root:

```
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-secret-key
DB_NAME=job_board_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

Install `python-dotenv`:

```bash
pip install python-dotenv
```

Load it in `manage.py` and `wsgi.py` (before setting `DJANGO_SETTINGS_MODULE`):

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## ✅ 3. Install Gunicorn

In your virtual environment:

```bash
pip install gunicorn
```

---

## ✅ 4. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This will put static files in `staticfiles/` as defined in `STATIC_ROOT`.

---

## ✅ 5. Migrate Database

```bash
python manage.py migrate
```

---

## ✅ 6. Run Gunicorn (Test First)

Test Gunicorn in the foreground:

```bash
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --env DJANGO_SETTINGS_MODULE=config.settings.production
```

If it runs without errors, proceed to run it as a system service.

---

## ✅ 7. Set Up Gunicorn as a Service

Create the service file:

```bash
sudo nano /etc/systemd/system/yourproject.service
```

Paste this (modify paths!):

```ini
[Unit]
Description=Gunicorn daemon for Django project
After=network.target

[Service]
User=youruser
Group=www-data
WorkingDirectory=/home/youruser/yourproject
ExecStart=/home/youruser/venv/bin/gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 \
  --env DJANGO_SETTINGS_MODULE=config.settings.production

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable yourproject
sudo systemctl start yourproject
```

Check status:

```bash
sudo systemctl status yourproject
```

---

## ✅ 8. Set Up Nginx

Install Nginx:

```bash
sudo apt install nginx
```

Create config:

```bash
sudo nano /etc/nginx/sites-available/yourproject
```

Paste:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /home/youruser/yourproject;
    }

    location /media/ {
        root /home/youruser/yourproject;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

Enable it:

```bash
sudo ln -s /etc/nginx/sites-available/yourproject /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ✅ 9. Add SSL (Optional but Highly Recommended)

Install Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
```

Run:

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Auto-renewal:

```bash
sudo systemctl enable certbot.timer
```

---

## ✅ 10. Firewall (if needed)

Allow Nginx:

```bash
sudo ufw allow 'Nginx Full'
```

---

## ✅ 11. Directory Permissions

Make sure the static/media folders and logs directory are owned by the correct user:

```bash
sudo chown -R youruser:www-data /home/youruser/yourproject
```

---

## ✅ Quick Summary of Commands

```bash
# Activate virtualenv
source ~/venv/bin/activate

# Load environment variables
export DJANGO_SETTINGS_MODULE=config.settings.production

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn manually
gunicorn config.wsgi:application --bind 127.0.0.1:8000

# OR run with systemd
sudo systemctl start yourproject
sudo systemctl enable yourproject

# Configure and restart Nginx
sudo nginx -t
sudo systemctl restart nginx

# (Optional) Add SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🧪 Final Check

* Visit `http://yourdomain.com` → should show your site.
* Visit `https://yourdomain.com` → should work with SSL (if configured).
* Check logs:

  * Nginx: `/var/log/nginx/error.log`
  * Gunicorn/Django: `logs/django.log` (if configured)

---
---

## Project Structure Reminder

```
config/
└── settings/
    ├── __init__.py
    ├── base.py
    ├── development.py
    ├── production.py
    ├── staging.py
    └── testing.py
```

Each environment file (e.g. `development.py`, `staging.py`) should **import from `base.py`** and override settings like `DEBUG`, `ALLOWED_HOSTS`, and DB info.

---

## 🧪 1. Running in **Development**

### ✅ Step 1: Create `development.py` (if not done)

File: `config/settings/development.py`

```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### ✅ Step 2: Set environment

You can run Django using this settings module by either:

#### Option A: Use `--settings` flag

```bash
python manage.py runserver --settings=config.settings.development
```

#### Option B: Set environment variable

```bash
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py runserver
```

---

## 🌐 2. Running in **Staging**

### ✅ Step 1: Create `staging.py`

File: `config/settings/staging.py`

```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['staging.yourdomain.com']

# Optional: point to a staging database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("STAGING_DB_NAME", "job_board_staging"),
        "USER": os.getenv("STAGING_DB_USER", "postgres"),
        "PASSWORD": os.getenv("STAGING_DB_PASSWORD", "admin123"),
        "HOST": os.getenv("STAGING_DB_HOST", "localhost"),
        "PORT": os.getenv("STAGING_DB_PORT", "5432"),
    }
}
```

### ✅ Step 2: Run using staging settings

#### Option A: One-liner:

```bash
DJANGO_SETTINGS_MODULE=config.settings.staging gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

#### Option B: Set the environment:

```bash
export DJANGO_SETTINGS_MODULE=config.settings.staging
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

#### Option C: Use `manage.py runserver` (if testing locally)

```bash
python manage.py runserver --settings=config.settings.staging
```

---

## 📝 Optional: Use `.env` Files for Each Environment

Use different `.env` files per environment, like:

* `.env.development`
* `.env.staging`
* `.env.production`

Then load the correct one using `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv(dotenv_path=BASE_DIR / '.env.development')  # or .env.staging
```

---

## ✅ Summary

| Environment | File                             | Command Example                                                                      |
| ----------- | -------------------------------- | ------------------------------------------------------------------------------------ |
| Development | `config/settings/development.py` | `python manage.py runserver --settings=config.settings.development`                  |
| Staging     | `config/settings/staging.py`     | `DJANGO_SETTINGS_MODULE=config.settings.staging gunicorn config.wsgi:application`    |
| Production  | `config/settings/production.py`  | `DJANGO_SETTINGS_MODULE=config.settings.production gunicorn config.wsgi:application` |

Each one just changes the `DJANGO_SETTINGS_MODULE`.

---

Would you like me to generate default contents for `development.py` and `staging.py` based on your `base.py` file, ready to copy-paste?


# add .env to .gitignore
- echo ".env" >> .gitignore

# Create the database user
sudo -u postgres psql -c "CREATE USER jobboard_user WITH PASSWORD 'Cityzen4';"

# Create the database
sudo -u postgres psql -c "CREATE DATABASE jobboard_dev;"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE jobboard_dev TO jobboard_user;"

# find a file
find /home/bk/Programming/ALX/alx-project-nexus/job-board/django-backend -name ".env*" -type f -exec ls -la {} \;