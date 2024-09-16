generate:
	@echo "Making migrations"
	python manage.py, makemigrations

migrate:
	@echo "Committing migrations to database"
	python manage.py migrate

runserver:
	@echo "Run web server"
	python manage.py runserver