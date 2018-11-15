# CASVAL REM (CASVAL Remote Execution Module)


## Deploy

```
$ terraform init -reconfigure
$ terraform apply
```

The terraform commands require settings of `aws_access_key`, `aws_secret_key` and `stage` to deploy through environment variables.

### Configuration

CASVAL dynamically generates Chalice's configuration file with Terraform's `.tfstate` file. If you would like to change configuration file ,though it's not mandatory, please modify `config.json` file in the root directory and invoke `python .chalice/config_gen.py`. This means that DO NOT CHANGE `.chalice/config.json` DIRECTRY.

### Administrator Password Hash Generation

The default administrator password of CASVAL is `admin123`. If you would like to change the password, you need to calculate a password hash and store it to the `ADMIN_PASSWORD_HASH` in `config.json`.
Below is an example of password hash for `admin123`. Then you may get the password hash `1f1eb4713b3d5e9ede7848207152b52fd6ed763f9818856d121dcdd6bf31c4f1`.

```
import binascii
import hashlib

PASSWORD_HASH_ALG = "sha256"
PASSWORD_SALT = "a93bae912d8740c0bfddb4ec33417bf7"
PASSWORD_ITERATION = 1000

password = "admin123"
token = binascii.hexlify(
    hashlib.pbkdf2_hmac(
        PASSWORD_HASH_ALG, password.encode(), PASSWORD_SALT.encode(), PASSWORD_ITERATION
    )
).decode("utf-8")
print(token)
```

## For Developers

### Local Testing

```
docker run -e MYSQL_DATABASE=casval_local -e MYSQL_ROOT_PASSWORD=admin123 -d -p 3306:3306 mysql:5.6 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
pipenv shell
pipenv install -d
pipenv install -d pip==10.0.1
chalice local --port 3000 --stage local
```
Note that pip 10.0.1 is required by chalice.


### Code Check

```
pipenv run unused app.py
pipenv run unused chalicelib/apis/*
pipenv run unused chalicelib/batches/*
pipenv run unused chalicelib/core/*
pipenv run unused chalicelib/core/stub/*
pipenv run fmt app.py
pipenv run fmt chalicelib/
pipenv run imports app.py
pipenv run imports chalicelib/
pipenv run lint app.py
pipenv run lint chalicelib/
```

### Code Update
```
pre-commit install
```

### Generate requirements.txt

```
pipenv lock -r > requirements.txt # is packages only
pipenv lock -r --dev > dev-requirements.txt # is dev-packages only
```
