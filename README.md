# CASVAL REM (CASVAL Remote Execution Module)


## Deploy

### Production (on Google App Engine)

```
terraform init
terraform apply
pipenv run config
pipenv run freeze
pipenv run deploy
```

### Local Development

```
docker run -e MYSQL_DATABASE=casval -e MYSQL_ROOT_PASSWORD=Passw0rd! -d -p 3306:3306 mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
pipenv shell
pipenv install -d
pipenv run server
```


## For Developers

### Code Formatter

```
pipenv run format
```
