# Database Setup Script for Photo Enhancer (Windows)

Write-Host "================================" -ForegroundColor Green
Write-Host "Photo Enhancer - Database Setup" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "manage.py")) {
    Write-Host "Error: manage.py not found. Please run this script from the Backend directory." -ForegroundColor Red
    exit 1
}

Write-Host "1. Creating migrations for accounts app..." -ForegroundColor Cyan
python manage.py makemigrations accounts
Write-Host ""

Write-Host "2. Applying migrations to database..." -ForegroundColor Cyan
python manage.py migrate
Write-Host ""

Write-Host "3. Checking stored users in database..." -ForegroundColor Cyan
python manage.py check_users
Write-Host ""

Write-Host "================================" -ForegroundColor Green
Write-Host "Database Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create a superuser: python manage.py createsuperuser"
Write-Host "2. Run the development server: python manage.py runserver"
Write-Host "3. Access admin panel: http://127.0.0.1:8000/admin/"
Write-Host "4. Check stored users: python manage.py check_users"
Write-Host "5. Check specific user: python manage.py check_users --username <username>"
