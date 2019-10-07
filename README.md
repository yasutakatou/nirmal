## ざっくりとした動かしかた。

pythonとhtmlは独立しているのでNetlifyにhtmlを置いて、pythonをGCPで動かすなど分けておけます。<BR>

python/nirmalを適当なフォルダに置いてpython nirmal.pyで動かします。<BR>
**(モジュールが足りなければ任意pipで入れてください。)**<BR>
rootで動かすとコマンド実行操作でヤバい自体が起きるのでガチガチの一般ユーザー推奨です。<BR>

www/htmlはnginxなどインストールしてhtml公開用ディレクトリにおいてください。<BR>
追加のJavaScriptモジュールとして<BR>

https://github.com/richtr/guessLanguage.js<BR>
 - _languageData.js
 - guessLanguage.js

https://github.com/usablica/intro.js<BR>
 - intro.js
 - introjs.css

この４つが必要なのでindex.htmlと同じところにおいてください。<BR>
あと*index.html*は静的に参照先を定義されちゃってるのでその部分の書き換えが必要です。<BR>

