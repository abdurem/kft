# KFT Agent Network

This project is a Django-based application for managing an agent network. It includes features for user authentication, product management, transaction history, and more.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.12
- pip (Python package manager)
- Docker and Docker Compose

## Setup Instructions

Follow these steps to set up and run the project:

### 1. Clone the Repository

```bash
git clone https://github.com/abdurem/kft.git
cd KFT
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Project Locally (SQLite)

1. Apply migrations:

   ```bash
   python manage.py migrate
   ```
2. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```
3. Start the development server:

   ```bash
   python manage.py runserver
   ```
4. Access the application at `http://127.0.0.1:8000`.

### 5. Run the Project with Docker (Postgres)

1. Build and start the Docker containers:

   ```bash
   docker-compose up --build
   ```
2. Access the application at `http://127.0.0.1:8000`.

### 6. API Documentation (Not Done Yet)

The project includes Swagger and Redoc for API documentation:

- Swagger: `http://127.0.0.1:8000/swagger/`
- Redoc: `http://127.0.0.1:8000/redoc/`

### 8. Getting Started

To get started, visit the following URLs:

- `/login`: Log in to your account.
- `/signup`: Create a new account.

## Project Structure

- `core/`: Contains the main application logic, including models, views, and serializers.
- `templates/`: HTML templates for the application.
- `staticfiles/`: Static assets like CSS and JavaScript.
- `kft_agent_network/`: Project-level settings and configurations.

## Notes

- The project is configured to use SQLite by default. If you want to switch to PostgreSQL, update the `DATABASES` setting in `kft_agent_network/settings.py`.
- Ensure the `.env` file is properly configured for sensitive settings like database credentials.

## License

This project is licensed under the MIT License.
