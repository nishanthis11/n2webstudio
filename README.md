# N2 Web Studio

Django site with public pages, a customer portal (`/portal/`) and a studio admin dashboard (`/studio/`).
Staff users (created with `createsuperuser`) are routed to the dashboard on login; everyone else goes to the portal.

## Windows PowerShell setup
```powershell
cd n2webstudio
py -m venv .venv
.\.venv\Scripts\Activate.ps1        # if blocked: Set-ExecutionPolicy -Scope Process Bypass
pip install -r requirements.txt
Copy-Item .env.example .env         # then edit DJANGO_SECRET_KEY
py manage.py makemigrations core
py manage.py migrate
py manage.py seed_content           # optional starter services, FAQs, labelled demo projects
py manage.py createsuperuser        # your own owner login — nothing is hardcoded
py manage.py collectstatic --noinput
py manage.py runserver
```
Open http://127.0.0.1:8000 · dashboard: /studio/ · raw Django admin: /django-admin/ · 404 preview (DEBUG): /404-preview/
