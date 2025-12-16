# TechOhr - Tech Company Platform & LMS

A complete technology company website and learning management system built with Django and TailwindCSS.

## Features

- **Company Website**: Services, Portfolio, Testimonials, Contact, About.
- **LMS (Learning Management System)**: Courses, Modules, Lessons, Progress Tracking, Enrollment.
- **Blog/CMS**: Posts, Categories, Tags, SEO optimization.
- **User Dashboard**: Student/Instructor dashboards.
- **Authentication**: Custom User model, Login, Register.
- **Responsive Design**: Mobile-first UI with TailwindCSS.

## Tech Stack

- **Backend**: Django 5
- **Frontend**: TailwindCSS (CDN), Alpine.js, HTML5
- **Database**: SQLite (default), extensible to PostgreSQL

## Setup Instructions

1.  **Clone the repository** (if not already done).
2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run migrations**:
    ```bash
    python manage.py migrate
    ```
5.  **Create a superuser** (for Admin access):
    ```bash
    python manage.py createsuperuser
    ```
6.  **Run the development server**:
    ```bash
    python manage.py runserver
    ```
7.  **Access the application**:
    - Website: `http://127.0.0.1:8000/`
    - Admin: `http://127.0.0.1:8000/admin/`

## Project Structure

- `core`: Main website pages (Home, Services, Contact).
- `courses`: LMS functionality (Courses, Lessons).
- `blog`: Blog and CMS.
- `users`: User authentication and dashboard.
- `templates`: HTML templates using TailwindCSS.
- `static`: Static assets (CSS, JS, Images).
- `media`: User-uploaded files (Course thumbnails, Profile pics).
