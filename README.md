# FurughiDonish - Smart Learning Platform

FurughiDonish is an intelligent learning platform that adapts to students' pace and learning style. The platform offers personalized learning paths in various subjects like mathematics, science, languages, and coding.

## Features

- **Adaptive Learning**: System adjusts difficulty based on student performance
- **Progress Tracking**: Detailed analytics and reports to visualize improvement
- **Gamification**: Badges and rewards to keep students motivated
- **Community Support**: Connect with peers and tutors for collaborative learning

## Tech Stack

- Django 5.0
- PostgreSQL (production) / SQLite (development)
- Bootstrap 5
- WhiteNoise for static files
- OpenAI and Gemini integrations

## Deployment on Render

### Prerequisites

- A Render account
- A GitHub repository with your project code

### Deployment Steps

1. Push your code to GitHub:
   ```
   git add .
   git commit -m "Prepare for Render deployment"
   git push
   ```

2. Log in to your Render account and create a new Web Service.

3. Connect your GitHub repository.

4. Configure the following settings:
   - **Name**: `furughidonish` (or your preferred name)
   - **Environment**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn tutorflow.wsgi:application`

5. Add the following environment variables:
   - `DJANGO_SECRET_KEY`: (generate a secure random string)
   - `DEBUG`: False
   - `OPENAI_API_KEY`: (your OpenAI API key)
   - `GEMINI_API_KEY`: (your Gemini API key)

6. If you want to use PostgreSQL, add a PostgreSQL database in the Render dashboard and it will automatically set the `DATABASE_URL` environment variable.

7. Deploy the service.

## Local Development

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - MacOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   DEBUG=True
   DJANGO_SECRET_KEY=your_secret_key
   OPENAI_API_KEY=your_openai_key
   GEMINI_API_KEY=your_gemini_key
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

## Project Structure

- `core/`: Main application with models, views, forms, and templates
- `tutorflow/`: Project settings and configuration
- `media/`: User-uploaded files (lesson resources, avatars, etc.)
