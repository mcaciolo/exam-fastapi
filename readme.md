# Exam FastAPI

Ma première application FastAPI


### Démarrage API

Pour lancer le serveur API depuis un environnement virtuel, suivez les étapes suivantes :

* Cloner ce répertoire (``git clone https://github.com/mcaciolo/exam-fastapi.git``)

* Si nécessaire, installez pipenv (``pip install --user pipenv``)

* Depuis le repertoire du projet, créer l'environnement virtuel : ``pipenv install`` 

* Lancez le serveur depuis l'environnement virtuel : ``pipenv run uvicorn main:api``

* Vérifiez l'état de fonctionnement de l'API : ``curl -X 'GET' 'http://localhost:8000/status' -H 'accept: application/json' -H 'Auth-header: alice:wonderland'``

* Demandez votre premier QCM : ``curl -X 'GET' 'http://localhost:8000/QCM' -H 'accept: application/json' -H 'Auth-header: alice:wonderland'``

## Documentation

Une fois le serveur API lancé, la documentation au format OpenAPI est accèssible à l'adresse : http://localhost/docs

## Auteur

Marcello CACIOLO


