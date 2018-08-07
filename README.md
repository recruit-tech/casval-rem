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
