# CASVAL REM (CASVAL Remote Execution Module)


## Deploy

```
pipenv run freeze
gcloud -q app deploy
```

## For Developers

### Code Formatter

```
pipenv run format
```

### Local Testing Environment

```
docker run -e MYSQL_DATABASE=casval -e MYSQL_ROOT_PASSWORD=admin123 -d -p 3306:3306 mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
export FLASK_APP='main.py'
export FLASK_ENV='development'
export SECRET_KEY='5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a'
export DB_NAME='casval'
export DB_USER='root'
export DB_PASSWORD='admin123'
export DB_ENDPOINT='127.0.0.1'
export DB_PORT='3306'
pipenv shell
pipenv install -d
pipenv run serve
```
