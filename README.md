# CASVAL REM (CASVAL Remote Execution Module)

## getstart
``
$ brew install pipenv
$ pipenv shell
$ pipenv install
```

## Local testing

```
$ chalice local --port 3000 --stage local
```

## Deploy (dev)

```
$ terraform init -reconfigure
$ terraform apply
```
Note that the terraform command requires setting of `aws_access_key` and `aws_secret_key` variables.


## Code check

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
If there is not error at the end okey.


## Administrator password hash generation

Below is an example to generate password of password `admin123`. Then, you can get `1f1eb4713b3d5e9ede7848207152b52fd6ed763f9818856d121dcdd6bf31c4f1` as the corresponding password hash. Set this value to the `ADMIN_PASSWORD_HASH` in `./chalice/config.json`.  

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