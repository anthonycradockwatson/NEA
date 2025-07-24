# AQA Computer Science NEA
## Description
This is the NEA for my AQA Computer Science A-level. It is the back-end for the AR startup Swappd which allows users to browse and view different car parts on their cars. This is not the current backend which has since changed, this is just what was submitted.
It is a database-centered backend, which is able to fully handle a range of different GET and POST requests, contains 2 different search algorithms (keyword and fuzzy search) and includes a complex recommendation system made from 2 subsystems, 1 being a weighting 
algorithm and one being a hybrid collaborative-content based system

# Modules used
 - Django
 - Psycopg2-binary
 - Numpy
 - pandas
 - Scikit-learn
 - Thefuzz
 - Nltk
 - Dotenv
 - Djangorestframework


## Installation and running
```bash
git clone https://github.com/anthonycradockwatson/NEA.git

cd NEA

python -m venv venv
venv\Scripts\activate          # Windows

pip install -r requirements.txt

cd NEA_project
python manage.py runserver

```
