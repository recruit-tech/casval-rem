# CASVAL REM (CASVAL Remote Execution Module)

## Getting Started

```
$ pipenv shell
$ pipenv install -d
$ pipenv install -d pip==10.0.1
$ chalice local --port 3000 --stage local

```
Note that pip 10.0.1 is required by chalice.

## Deploy (dev)

```
$ terraform init -reconfigure
$ terraform apply
```

Note that the terraform command requires setting of `aws_access_key` and `aws_secret_key` variables.

## Code Checking

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

## Make requirements.txt

```
pipenv lock -r > requirements.txt # is packages only
pipenv lock -r --dev > dev-requirements.txt # is dev-packages only
```

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

## Type check
How to check type. This is optional and is good.

### Configuration

```
# Make .pyre_configuration. aute create is (binary,source_directory, typeshed).
pyre init

# Change to apply to your environment
vim .pyre_configuration
```
example
```
{
  "binary": "/Users/takehaya/.local/share/virtualenvs/casval-rem-R9TrrDKY/bin/pyre.bin",
  "source_directories": [
    "."
  ],
   "do_not_check":[
   ".chalice",
   ".pyre",
    "terraform",
    "vendor"
  ],
  "search_path":[
    "/Users/takehaya/.local/share/virtualenvs/casval-rem-R9TrrDKY/lib/python3.6/site-packages/"
  ],
  "typeshed": "/Users/takehaya/.local/share/virtualenvs/casval-rem-R9TrrDKY/lib/pyre_check/typeshed/"
}
```
* search_path mean use package path.
* If you are using macOS and Pipenv you maybe use to the path of `$HOME/.local/share/virtualenvs/casval-rem-*/lib/python3.6/site-packages/`
### Usage
```
# do type check
pipenv run types
```
Troubleshooting this document :)
[pyre-check.org](https://pyre-check.org/)
