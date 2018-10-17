# 初期データ投入のやり方

* 以下のコマンドを使うとpython `./chalicelib/apis/fixtures/` ファイル内にある `*.json` のfixtureのデータを全て投入します．
```shell
python ./chalicelib/apis/fixtures/seed_requests.py seed
```

* 以下のコマンドを使うと全てのtableに対して削除を走らせることができる
```shell
python ./chalicelib/apis/fixtures/seed_requests.py drop
```