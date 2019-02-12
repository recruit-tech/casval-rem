# Unit Test

## Install
### pytest
```
pip install -U pytest
```
## Use
to command line
```
pytest . -s
```

`-s` is printing to enable option
## Your contribute Tips
This application has external services such as SQS and S3.
Testing cases involving these I think that you will probably write the test code using mock, stub, etc. in many cases.

Now time,[moto](https://github.com/spulec/moto)using test.

This basis how to write this use it as follows.
．
```python
from moto import mock_sqs

@mock_sqs
def testing_function():
    pass

```
This Decorator in so far as executed,it related to sqs are replaced by mock.
however, there is a problem with this.That does not mean that the instances are over and the data is not being saved.

Also, the return on the number of queues is done with environment variables as well. Also, if you do not use environment variables, registering `-1` in GEN_CREATE_QUEUE actually calculates in the mock.

```python
    def setup_class(self):
        db_seed()

    def teardown_method(self):
        SQSMock.dispose()
        S3Mock.dispose()
        os.environ["GEN_CREATE_QUEUE"] = str(0)
```