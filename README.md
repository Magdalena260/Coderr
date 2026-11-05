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

Replace `<repository-url>` with the URL of your GitHub repository.

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root directory.

Add the following variable:

```env
SECRET_KEY=your-own-secure-django-secret-key
```

Replace the placeholder with a secure Django secret key.

The `.env` file must not be committed to Git.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API will be available at:

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

Include the token in the HTTP request header:

```http
Authorization: Token YOUR_AUTH_TOKEN
```

The token is returned after successful registration or login.

## Running Tests

Run the project's Django tests with:

```bash
python manage.py test
```

## Django Administration

Create an administrator account:

```bash
python manage.py createsuperuser
```

Then open:

http://127.0.0.1:8000/admin/

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

## Security

The following files and directories are excluded from version control:

- `.env`
- `db.sqlite3`
- `.venv/`
- `__pycache__/`
- `media/`

Do not commit passwords, authentication tokens or secret keys to the repository.

## Project Information

This project was created as part of the Developer Akademie Fullstack Developer training program.