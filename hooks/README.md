# API Specification Test

## Test

### Install
#### dredd
Install with npm。  
If you faill to build, try lowering node version.

```
$ npm install -g dredd
```

#### dredd-hooks
Install dredd-hooks in order to run hook.
dredd-hooks is defined in Pipfile.thereby run `pipenv install -d` to auto install.

```
$ pipenv install -d
```

To enable shell to run `pipenv shell`. thereby installed enable libraries.   

```
$ pipenv shell
```

### Compiling apib
When compiling base.apib of casbal-doc with aglio, all combined file output, 
The path of rafflesia-doc is modified as case by case.

```
$ aglio -c -i ../../casval-doc/base.apib  -o all.apib
```

### Running dredd

```
$ dredd all.apib https:/localhost:3000 --language=python --hookfiles="./*.py"
```

## How to write skip
APIs defined by API Blueprint are all executed, so if there is an unimplemented API, the test will be dropped.
Therefore, for unimplemented API you need to write skip in hook file.


For instance,->

```
@hooks.before("Scan > スキャン情報 > 取得")
def skip_get_scan(transaction):
    transaction["skip"] = True
```

The string to be written after `@ hooks.before` corresponds to one API.
It can be examined by using the `--names` option of the dredd command.

```
$ dredd all.apib 127.0.0.1:3000 --language=python --names
info: Beginning Dredd testing...
info: Audit > 検査一覧の取得 > 検査一覧の取得
skip: GET (200) /audit?mode=unsubmitted&page=1&count=30
info: Audit > 新規検査の登録 > 新規検査の登録
skip: POST (200) /audit
info: Audit > 閲覧用トークンの生成 > 閲覧用トークンの生成
skip: POST (200) /audit/3cd708cefd58401f9d43ff953f063467/tokens
info: Audit > 検査情報 > 取得
skip: GET (200) /audit/3cd708cefd58401f9d43ff953f063467
info: Audit > 検査情報 > 更新
skip: PATCH (200) /audit/3cd708cefd58401f9d43ff953f063467
info: Audit > 検査情報 > 失効
skip: DELETE (200) /audit/3cd708cefd58401f9d43ff953f063467
info: Audit > 検査の提出 > 提出
skip: POST (200) /audit/3cd708cefd58401f9d43ff953f063467/submit
info: Audit > 検査の提出 > 取り下げ／却下 > Example 1
skip: DELETE (200) /audit/3cd708cefd58401f9d43ff953f063467/submit
info: Audit > 検査の提出 > 取り下げ／却下 > Example 2
skip: DELETE (200) /audit/3cd708cefd58401f9d43ff953f063467/submit
info: Scan > 新規スキャンの登録 > 新規スキャンの登録
skip: POST (200) /audit/3cd708cefd58401f9d43ff953f063467/scan
info: Scan > スキャン情報 > 取得
skip: GET (200) /audit/3cd708cefd58401f9d43ff953f063467/scan/21d6cd7b33e84fbf9a2898f4ea7f90cc
info: Scan > スキャン情報 > 更新
skip: PATCH (200) /audit/3cd708cefd58401f9d43ff953f063467/scan/21d6cd7b33e84fbf9a2898f4ea7f90cc
info: Scan > スキャン情報 > 削除
skip: DELETE (200) /audit/3cd708cefd58401f9d43ff953f063467/scan/21d6cd7b33e84fbf9a2898f4ea7f90cc
info: Scan > スキャンスケジュール > 更新
skip: PATCH (200) /audit/3cd708cefd58401f9d43ff953f063467/scan/21d6cd7b33e84fbf9a2898f4ea7f90cc/schedule
info: Scan > スキャンスケジュール > 削除
skip: DELETE (200) /audit/3cd708cefd58401f9d43ff953f063467/scan/21d6cd7b33e84fbf9a2898f4ea7f90cc/schedule
info: Auth > 管理者の認証 > 管理者の認証
skip: POST (200) /auth
info: Vulnerabilities > 脆弱性一覧の取得 > 脆弱性一覧の取得
skip: GET (200) /vulns?fix_required=false&before=1.3.6.1.4.1.25623.1.0.105879&count=30
info: Vulnerabilities > 脆弱性情報 > 取得
skip: GET (200) /vulns/1.3.6.1.4.1.25623.1.0.105879
info: Vulnerabilities > 脆弱性情報 > 修正要否の変更
skip: PATCH (200) /vulns/1.3.6.1.4.1.25623.1.0.105879
complete: 0 passing, 0 failing, 0 errors, 19 skipped, 19 total
complete: Tests took 198ms

...
```
