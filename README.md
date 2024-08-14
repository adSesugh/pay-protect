# PayProtect API
PayProtect is a mobile app that is focused on managing buyer and seller transaction ensuring that both parties are not played short of their appropriate values

#### Tech Stack used
- Python
- Django
- Django rest framework
- PostgreSQL

### How to use
- Clone the repo and cd into the root directory.
- Install all libraries using `pip install -r requirements.txt`
- Make a copy of the .env.example file and name it .env, then fill all the placeholders with the appropriate values.
- Migrate all models to database using this command `python manage.py migrate`
- To start app, run `python manage.py runserver` Then view api documentation in the browser [http://localhost:8000](`http://localhost:8000`)