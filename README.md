# CASVAL REM (CASVAL Remote Execution Module)


## Deploy

```
pipenv run freeze
pipenv run deploy
```

## For Developers

### Code Formatter

```
pipenv run format
```

### Local Testing Environment

```
docker run -e MYSQL_DATABASE=casval -e MYSQL_ROOT_PASSWORD="" -d -p 3306:3306 mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
export FLASK_APP='main.py'
export FLASK_ENV='development'
export SECRET_KEY='5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a'
pipenv shell
pipenv install -d
pipenv run serve
```
