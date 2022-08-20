# NFO Django
## Installation

Prepare python environment
```sh
apt-get install python3-venv
cd nusantarafood-django/server
python3 -m venv .venv
source .venv/bin/activate
```

Install python libraries
```sh
pip install django djangorestframework
pip install pandas nltk openpyxl pyldavis wikipedia
```

Migrate database and create admin
```sh
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

Run import commands
```sh
python manage.py importjl /home/amir/assets/jl
python manage.py fixdocumenttitle
python manage.py importwiki /home/amir/assets/wiki
python manage.py wordnet -i aziekitchen-udang -s /home/amir/assets/stopwords.txt -t 7 -p 20
```

- Imports downloaded content from .jl files
- Clean document (the contents) title. Remove unwanted characters like ... or ~
- Imports recipe definitions (id, ms, en) and categories from .xlsx
- Run LDA model and get hypernyms using Wordnet

# Run development server
```sh
python manage.py runserver
```

To view django admin. Browse to http://localhost:8000/admin
Login with username and password from `createsuperuser` command
