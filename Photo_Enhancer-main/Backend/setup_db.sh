#!/bin/bash
# Database Setup Script for Photo Enhancer

echo "================================"
echo "Photo Enhancer - Database Setup"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the Backend directory."
    exit 1
fi

echo "1. Creating migrations for accounts app..."
python manage.py makemigrations accounts
echo ""

echo "2. Applying migrations to database..."
python manage.py migrate
echo ""

echo "3. Checking stored users in database..."
python manage.py check_users
echo ""

echo "================================"
echo "Database Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Create a superuser: python manage.py createsuperuser"
echo "2. Run the development server: python manage.py runserver"
echo "3. Access admin panel: http://127.0.0.1:8000/admin/"
echo "4. Check stored users: python manage.py check_users"
echo "5. Check specific user: python manage.py check_users --username <username>"
