
# Coderr Backend

Coderr is a REST API backend for a service marketplace, developed with Django and Django REST Framework.

The application allows business users to publish service offers and customers to place orders and submit reviews.

## Technologies

- Python
- Django
- Django REST Framework
- SQLite
- Token Authentication
- Pillow
- python-dotenv

## Features

- User registration and login
- Customer and business profiles
- Profile management
- Service offers with three pricing tiers
- Order management
- Customer reviews
- Business order statistics
- General platform statistics

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd coderr
```

Replace `<repository-url>` with the URL of the GitHub repository.

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root directory, alongside `manage.py`.

Add the following variable:

```env
DJANGO_SECRET_KEY=your-own-secure-django-secret-key
```

Replace the placeholder with a secure Django secret key.

The `.env` file contains sensitive information and must not be committed to Git.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

The development server will be available at:

http://127.0.0.1:8000/

## API Endpoints

### Authentication and Profiles

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/registration/` | Register a user |
| POST | `/api/login/` | Log in |
| GET, PATCH | `/api/profile/<id>/` | Retrieve or update a profile |
| GET | `/api/profiles/business/` | List business profiles |
| GET | `/api/profiles/customer/` | List customer profiles |

### Offers

| Method | Endpoint | Description |
|---|---|---|
| GET, POST | `/api/offers/` | List or create offers |
| GET, PATCH, DELETE | `/api/offers/<id>/` | Retrieve, update or delete an offer |
| GET | `/api/offerdetails/<id>/` | Retrieve offer details |

### Orders

| Method | Endpoint | Description |
|---|---|---|
| GET, POST | `/api/orders/` | List or create orders |
| GET, PATCH, DELETE | `/api/orders/<id>/` | Retrieve, update or delete an order |
| GET | `/api/order-count/<business_id>/` | Count active business orders |
| GET | `/api/completed-order-count/<business_id>/` | Count completed business orders |

### Reviews

| Method | Endpoint | Description |
|---|---|---|
| GET, POST | `/api/reviews/` | List or create reviews |
| PATCH, DELETE | `/api/reviews/<id>/` | Update or delete a review |

### General Information

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/base-info/` | Retrieve general platform statistics |

## Authentication

Protected API endpoints require token authentication.

After logging in, use the returned authentication token in the HTTP request header:

```http
Authorization: Token YOUR_AUTH_TOKEN
```

Replace `YOUR_AUTH_TOKEN` with the actual token.

Access to protected endpoints depends on the authenticated user's role and permissions.

## Running Tests

Run the project's Django tests with:

```bash
python manage.py test
```

Check the Django configuration:

```bash
python manage.py check
```

Check whether new migrations are required:

```bash
python manage.py makemigrations --check --dry-run
```

Check whether database migrations are pending:

```bash
python manage.py migrate --check
```

## Code Quality

The project uses Ruff for basic Python code quality checks.

Run:

```bash
python -m ruff check . --select E,F --exclude migrations
```

This checks selected Python style rules and common errors.

## Django Administration

Create an administrator account:

```bash
python manage.py createsuperuser
```

Start the development server and open:

http://127.0.0.1:8000/admin/

Log in using the administrator credentials.

## Project Structure

```text
coderr/
├── auth_app/
├── core/
├── offers_app/
├── orders_app/
├── reviews_app/
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Applications

**auth_app**

Handles user registration, login, authentication and profile management.

**offers_app**

Manages service offers and their associated pricing details.

**orders_app**

Handles customer orders, order status updates and business order statistics.

**reviews_app**

Manages customer reviews and ratings.

**core**

Contains the main Django project configuration, including settings and URL routing.

## Security

The following files and directories should be excluded from version control:

- `.env`
- `db.sqlite3`
- `.venv/`
- `__pycache__/`
- `media/`

Never commit passwords, authentication tokens or secret keys to the repository.

The Django secret key is loaded from the `.env` file using `python-dotenv`.

The application is configured for local development. Production deployment requires additional security configuration, including appropriate debug settings, allowed hosts and secure secret management.

## Project Information

This project was created as part of the Developer Akademie Fullstack Developer training program.

The goal of the project is to implement a RESTful backend using Django and Django REST Framework, including authentication, permissions, database models, serializers, API views and automated tests.
