# to run the application 
pip install -r requirements.txt

# make migrations 

python manage.py makemigrations

# Exporting ALLOWED_HOSTS for Django
export ALLOWED_HOSTS="127.0.0.1,localhost"


# run the application

python manage.py runserver


