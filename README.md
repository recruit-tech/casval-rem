# CASVAL REM (CASVAL Remote Execution Module)


## Deploy

```
$ pipenv lock -r > requirements.txt
$ gcloud -q app deploy
```


## For Developers

### Local Testing

```
docker run -e MYSQL_DATABASE=casval_local -e MYSQL_ROOT_PASSWORD=admin123 -d -p 3306:3306 mysql:5.6 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
pipenv shell
pipenv install -d
FLASK_APP=main.py FLASK_ENV=development flask run
```


### Code Check

```
pipenv run unused main.py
pipenv run unused apis/*
pipenv run fmt main.py
pipenv run fmt apis/
pipenv run imports main.py
pipenv run imports apis/
pipenv run lint main.py
pipenv run lint apis/
```

### Code Update
```
pre-commit install
```
