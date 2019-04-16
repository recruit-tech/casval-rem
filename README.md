# CASVAL REM (CASVAL Remote Execution Module)


## Deploy

```
pipenv lock -r > requirements.txt
gcloud -q app deploy
```

## For Developers

### Code Formatter

```
pipenv run format
```

### Local Testing Environment

```
docker run -e MYSQL_DATABASE=casval_local -e MYSQL_ROOT_PASSWORD=admin123 -d -p 3306:3306 mysql:5.6 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
pipenv shell
pipenv install -d
pipenv run serve
```
