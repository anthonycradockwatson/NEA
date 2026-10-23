# AQA Computer Science NEA
## Description
NEA Project for my Computer Science A-Level. It is a Python RESTful API Backend using a normalised relational PostgreSQL Database with the key complex features being the custom search and recommendation algorithm. 

## Key Features & Architecture

- **Django & PostgreSQL API:** Built a object-oriented Python web API capable of complex SQL/JSON query handling, secure user authentication, and a dynamic recommendation engine.
- **Nginx & Gunicorn Deployment:** Set up request routing and a reverse proxy configuration using Gunicorn and Nginx to ensure production-grade reliability and performance.
- **Custom Levenshtein Search Engine:** Developed a fuzzy search algorithm from scratch using Levenshtein Distance with a configurable similarity threshold for accurate, error-tolerant queries.
- **Defensive Security & Input Validation:** Implemented strict input sanitization, parameterized database queries, and defensive programming checks to prevent common web vulnerabilities (e.g., SQL injection, XSS).

## Modules used
 - Django
 - Psycopg2-binary
 - Numpy
 - pandas
 - Scikit-learn
 - Thefuzz
 - Nltk
 - Dotenv
 - Django Rest Framework

## Recommendation and Search Algorithm
### 1. Custom Levenshtein Fuzzy Search
To handle typos, partial matches, and variations in user queries without relying on heavy external search libraries, I engineered a custom search engine from scratch:
* **Algorithm Core:** Computes the Levenshtein edit distance between the query string and database records.
* **Dynamic Similarity Threshold:** Implements a configurable cutoff threshold to balance precision and recall, ensuring users get relevant results even with minor spelling errors.
* **Performance Optimization:** Optimized text-preprocessing and indexing passes to minimize latency during query evaluation.

### 2. Dynamic Recommendation System
The application features a built-in recommendation engine designed to surface relevant content dynamically:
* **OOP-Driven Architecture:** Built using modular object-oriented principles to cleanly decouple data retrieval from recommendation logic.
* **SQL & JSON Integration:** Aggregates user interaction data and metadata stored via SQL queries and JSON payloads to generate personalized suggestions.

<img width="1600" height="1000" alt="image" src="https://github.com/user-attachments/assets/32be47b1-a7f4-4ffe-8c1d-fe5192dc6ba0" />


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
