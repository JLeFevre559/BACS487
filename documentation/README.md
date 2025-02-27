# Financial Education Platform

## Overview
A Django-based web application designed to provide interactive financial education through various learning modules, progress tracking, and personalized learning paths.

## Documentation Structure

### Getting Started
- [Installation Guide](getting-started/installation.md)
- [Configuration Guide](getting-started/configuration.md)
- [Deployment Guide](getting-started/deployment.md)

### Architecture
- [System Overview](architecture/overview.md)
- [Database Models](architecture/models.md)
- [Views and Logic](architecture/views.md)
- [Forms](architecture/forms.md)
- [URL Structure](architecture/urls.md)

### Features
- [User Management](features/user-management.md)
- [Learning Modules](features/learning-modules.md)
- [Progress Tracking](features/progress-tracking.md)
- [Permissions System](features/permissions.md)

### Testing
- [Testing Overview](testing/overview.md)
- [Unit Tests](testing/unit-tests.md)

### Development
- [Changelog](development/changelog.md)

## Quick Start

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Key Features

- Interactive learning modules for financial education
- Progress tracking and experience point system
- Multiple choice questions with difficulty levels
- User management system with role-based permissions
- Category-based learning paths
- Financial market data integration

## Technology Stack

- Django
- Python
- PostgreSQL
- Crispy Forms
- Bootstrap