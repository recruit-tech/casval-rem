# CASVAL REM (CASVAL Remote Execution Module)

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
black --py36 --line-length 110 app.py
black --py36 --line-length 110 chalicelib/
black --py36 --line-length 110 chalicelib/apis/
black --py36 --line-length 110 chalicelib/batches/
black --py36 --line-length 110 chalicelib/core/
flake8 app.py
flake8 chalicelib/
isort app.py
isort -rc chalicelib/
```