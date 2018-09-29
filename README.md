# CASVAL REM (CASVAL Remote Execution Module)


## Deployment

```
$ terraform init -reconfigure
$ terraform apply
```

The terraform commands require settings of `aws_access_key`, `aws_secret_key` and `stage` to deploy through environment variables.


## Local Execute

```
$ docker run -e MYSQL_DATABASE=casval_local -e MYSQL_ROOT_PASSWORD=admin123 -d -p 3306:3306 mysql:5.6
$ pipenv shell
$ pipenv install -d
$ pipenv install -d pip==10.0.1
$ chalice local --port 3000 --stage local
```
Note that pip 10.0.1 is required by chalice.

## seed
```
# db table create
python seed_enrty.py create

# db table drop
python seed_enrty.py drop

# db table create & seed
python seed_enrty.py seed
```

## Configuration
It is necessary to dynamically generate configuration based on tfstate etc. Here we show these methods.

As for what is involved in production...
* `config_gen.py`: Config generation script
* `terafform.tfstate`: Original data of information used for configuration
* `config.json`: Model file for automatically generating contents. Embedded variables are available.

### Example
#### Generate method
```
$ pwd　# /casval-rem/.chalice
$ python config_gen.py
```

#### Defining Embedded Variables

* `__<id_1>__<id_2>`: Embedded variable
* `<id_1>`: All other than these are regarded as fixed values on the user side and are not replaced

#### Examples of embedded variables
`config.json`(user setting)
```
....
    "dev": {
      "environment_variables": {
         ....
        "DB_USER":"__dev__database_username",
        "DB_PASSWORD":"__dev__database_password",
        "DB_PORT":"3306"
      }
    },
....
```
`terraform.tfstate`
```
....
"outputs": {
    "bucket": {
        "sensitive": false,
        "type": "string",
        "value": "casval-dev20180827071622708900000001"
    },
    "database_name": {
        "sensitive": false,
        "type": "string",
        "value": "casval_dev"
    },
    "database_password": {
        "sensitive": false,
        "type": "string",
        "value": "admin123"
    },
....
```



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
