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

### How to use social media Authentication
- Login to admin panel to create a client ID and client Secret under application
- Copy the client ID 
- ### For Google Auth
  `
    curl -X POST -d "grant_type=convert_token&client_id=<django-oauth-generated-client_id>&backend=google-oauth2&token=<google_token>" http://uri:port/auth/convert-token
  `
- ### For Facebook Auth
  `
   curl -X POST -d "grant_type=convert_token&client_id=<client_id>&backend=facebook&token=<facebook_token>" http://uri:port/auth/convert-token
  `
- ### For Instagram Auth
  `
   curl -X POST -d "grant_type=convert_token&client_id=<django-oauth-generated-client_id>&backend=instagram&token=<access_token>" http://uri:port/auth/convert-token
  `