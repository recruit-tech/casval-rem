import os

path = os.path.abspath(".")

output_json_path = "/.chalice/config.json"


def load_env(env_name):
    print("your selected env: " + env_name)
    try:
        eval(env_name)()
    except Exception as e:
        print(e)
        print("your selected env: not found")


def test_env():
    os.environ['DB_NAME'] = 'casval_local'
    os.environ['DB_USER'] = 'root'
    os.environ['DB_PASSWORD'] = 'admin123'
    os.environ['DB_ENDPOINT'] = 'localhost'
    os.environ['DB_PORT'] = '3306'
    os.environ["PASSWORD_HASH_ALG"] = 'sha256'
    os.environ["MAX_COMMENT_LENGTH"] = '1000'
    os.environ["MIN_SCAN_DURATION_IN_SECONDS"] = '2'
    os.environ["SCAN_SCHEDULABLE_DAYS_FROM_NOW"] = '10'
    os.environ["SCAN_SCHEDULABLE_DAYS_FROM_START_DATE"] = '5'
    os.environ["AWS_IP_RANGES_URL"] = '127.0.0.0/8'
