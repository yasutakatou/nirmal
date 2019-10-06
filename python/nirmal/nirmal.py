#!/usr/bin/env python
# coding:utf-8

PORT=2960

from gensim.models.doc2vec import Doc2Vec
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from datetime import datetime
import cgi
import os
import os.path
import requests
import subprocess32 as subprocess
#import subprocess
import sys
import urlparse

# 実行パス取得
PATH = os.path.dirname(os.path.abspath(__file__))
print 'PATH: ' + PATH

#全行読み込み
def readsearch(filename):
  f = open(PATH + '/' + filename)
  data = f.read()
  f.close()
  return data

#空ファイルを作る、または文字列をセットされたらファイルに書き込む
def fcreate(filename, string):
  f = open(PATH + '/' + filename,'w')
  if len(string) > 0:
    f.write(string + '\n')
  f.close()

def start(port, callback):
    def handler(*args):
        CallbackServer(callback, *args)
    server = HTTPServer(('', int(port)), handler)
    server.serve_forever()

class CallbackServer(BaseHTTPRequestHandler):
    def __init__(self, callback, *args):
        self.callback = callback
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        query = parsed_path.query
        self.send_response(200)
        self.wfile.write("Access-Control-Allow-Origin: *\nContent-type: text/plain\n\n");
        self.end_headers()
        result = self.callback(query)
        self.wfile.write('\r\n'.join(result))
        return result

    def do_POST(self):
        self.send_response(200)
        self.wfile.write("Access-Control-Allow-Origin: *\nContent-type: text/plain\n\n");
        self.end_headers()
        os.environ['REQUEST_METHOD'] = 'POST'
        form = cgi.FieldStorage(self.rfile, self.headers)
        print form
        # POSTされるパラメータを変数に格納。変数は以下
        # ctrl: 動作種類を指定
        # user: ユーザー名を指定
        # typa: モード(Code / Document)を指定
        # typb: モード配下の何を操作するかを指定
        # code: POSTされるコードやデータを指定
        for key in form.keys():
          value = form.getvalue(key,'')
          exec '%s = """%s"""' % (key,value)
        # ブラウザに返す文字列をresultにまとめる
        result = ctrl + ' success'
        if (ctrl == 'repo'):
          # リポジトリにコミットしてファイル作成。元のマスターを日付に改名。
          data = readsearch('custom/' + user + '/' + typa + '/index')
          lines = data.split("\n")
          for check in lines:
            if len(check) > 1:
              params = check.split("\t")
              if (params[1] == typb):
                daystr = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                os.rename(PATH + '/custom/' + user + '/' + typa + '/' + params[0] + '.c', PATH + '/custom/' + user + '/' + typa + '/' + params[0] + '.' + daystr)
                fcreate('custom/' + user + '/' + typa + '/' + params[0] + '.c', code)
        elif (ctrl == 'gcom'):
          # Global Wordをコミットしてファイル作成。元ファイルは削除
          os.remove(PATH + '/custom/' + user + '/' + typa + '/gword')
          fcreate('custom/' + user + '/' + typa + '/gword', code)
        elif (ctrl == 'comren'):
          # コード名を変更。chgsに格納しつつインデックスで同じ名前のものを置き換えてファイル作成。
          chgs = ''
          data = readsearch('custom/' + user + '/' + typa + '/index')
          lines = data.split("\n")
          for check in lines:
            if len(check) > 1:
              params = check.split("\t")
              if (params[1] == typb):
                chgs = chgs + params[0] + '\t' + code + '\n'
              else:
                chgs = chgs + check + '\n'
          os.remove('custom/' + user + '/' + typa + '/index')
          fcreate('custom/' + user + '/' + typa + '/index', chgs)
        elif (ctrl == 'guess'):
          # POSTされたコードをDoc2Vecでpublicのコードリポジトリから類似を探し、結果を戻り値で返す。
          # この部分だけ戻り値をjavascriptで加工する。類似文の学習は別途実施が必要(train.py)
          training_docs = []
          words = []
          ext = ''
          csvs = code.split("\n")
          for dat in csvs:
            words.append(dat)
          model = Doc2Vec.load(PATH + '/doc2vec.model')
          test_docvec = model.infer_vector(words)
          for sim_doc in model.docvecs.most_similar([test_docvec]):
            ext = ext + '<li class="dcode">\r';
            ext = ext + '<h3 class="dmenu"><li>' + sim_doc[0] + '</li><li>' + str(sim_doc[1]) + '</h3></li>\r'
            ext = ext + subprocess.check_output('FILE=`grep "' + sim_doc[0] + '" ./public/index | cut -f 1` ; cat ./public/$FILE.a | tail -n +2 | head -10', shell=True)
            ext = ext + '</li>\r'
          self.wfile.write(ext)
          return
        elif (ctrl == 'run'):
          # POSTされたコードを一行ずつ実行して結果を戻り値で返す。エラーの場合は空。
          ext = '<li class="dcode">\r';
          cmdlist = code.split("\n")
          for dat in cmdlist:
              ext = ext + '<h3 class="dmenu"><li>' + dat + '</li></h3>\r'
              ext = ext + subprocess.check_output(dat, shell=True,timeout=60) + '\r'
              ext = ext + '</li>\r'
          self.wfile.write(ext)
          return
        self.wfile.write(result)
        return

def callback_method(query):
    print 'query: ' + query
    # ブラウザに返す文字列をresultにまとめる
    result = ''
    strs = ''
    # パラメータを分割しアレイ化する
    params = query.split("=")
    if params[0].find('comcode') != -1:
      # 現在のマスターを現在日時を付けてリネームし、Commitされたファイルをマスター名にリネームする
      # [1]: ユーザー名
      # [2]: モード(Code / Document)
      # [3]: id=comX:YのX。リポジトリ格納順を示す
      daystr = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
      os.rename(PATH + '/custom/' + params[1] + '/' + params[2] + '/' + params[3].split(".")[0] + '.c', PATH + '/custom/' + params[1] + '/' + params[2] + '/' + params[3].split(".")[0] + '.' + daystr)
      os.rename(PATH + '/custom/' + params[1] + '/' + params[2] + '/' + params[3], PATH + '/custom/' + params[1] + '/' + params[2] + '/' + params[3].split(".")[0] + '.c')
      result = 'Commit success'
    elif params[0].find('delcode') != -1:
      # ブランチを消す場合はそのまま消す。マスターを消す場合はブランチがあれば最新のブランチをマスターに昇格。ブランチが無ければインデックスからも消す。
      # [1]: ユーザー名
      # [2]: モード(Code / Document)
      # [3]: id=comX:Y。リポジトリ格納順とリポジトリ順を示す
      counts = int(params[3].split(".")[0])
      ccnt = 1
      owl = ''
      data = readsearch('custom/' + params[1] + '/' + params[2] + '/index')
      lines = data.split("\n")
      for check in lines:
        if (counts == ccnt):
          owl = int(check.split("\t")[0])
        ccnt = ccnt + 1
      if (params[3].split(".")[1] == '0'):
        ret = subprocess.check_output('ls -tr1 ' + PATH + '/custom/' + params[1] + '/' + params[2] + '/' + str(owl) + '.* | grep -v .[a,c]$ | head -1', shell=True)
        if len(ret) > 1:
          os.remove(PATH + '/custom/' + params[1] + '/' + params[2] + '/' + str(owl) + '.c')
          os.rename(ret.rstrip(),PATH + '/custom/' + params[1] + '/' + params[2] + '/' + str(owl) + '.c')
        else:
          data = readsearch('custom/' + params[1] + '/' + params[2] + '/index')
          lines = data.split("\n")
          ccnt = 1
          strs = ''
          for check in lines:
            if (not ccnt == owl):
              if len(check) > 1:
                strs = strs + check + '\n'
            ccnt = ccnt + 1
          os.remove(PATH + '/custom/' + params[1] + '/' + params[2] + '/index')
          fcreate('custom/' + params[1] + '/' + params[2] + '/index', strs)
          os.remove(PATH + '/custom/' + params[1] + '/' + params[2] + '/' + str(owl) + '.c')
      else:
        os.remove(PATH + '/custom/' + params[1] + '/' + params[2] + '/' + params[3])
      result = 'delete success'
    elif params[0].find('repolist') != -1:
      # リポジトリリスト画面のHTMLを生成して戻す。メニューボタンも含めたHTMLタグも生成するのでそのまま表示。
      # [1]: ユーザー名
      # [2]: モード(Code / Document)
      data = readsearch('custom/' + params[1] + '/' + params[2] + '/index')
      lines = data.split("\n")
      cod = 1
      for check in lines:
        if len(check) > 1:
          codz = check.split("\t")
          result = result + '<span class="' + str(cod) + ':0" >' + codz[1].replace('\n','') + '</li>\r'
          result = result + subprocess.check_output('ls -tr1 ' + PATH + '/custom/' + params[1] + '/' + params[2] + '/' + codz[0] + '.* | grep -v .[a,c]$ | cut -d . -f 2', shell=True)
          cod = cod + 1
    elif params[0].find('index') != -1:
      # public/custom/documentのインデックスを取得し戻す。
      # [1]: モード(Code / Document)
      # [2]: ユーザー名
      if params[1].find('public') != -1:
        result = readsearch('public/index')
      elif params[1].find('customc') != -1:
        result = readsearch('custom/' + params[2] + '/cod/index')
      else:
        result = readsearch('custom/' + params[2] + '/doc/index')
    elif params[0].find('auth') != -1:
      # ユーザ－のフォルダがあるかどうかで認証する。なければfailを返す。
      # [1]: ユーザー名
      if (os.path.exists(PATH + '/custom/' + params[1])):
        result = 'true'
      else:
        result = 'fail'
    elif params[0].find('cnew') != -1 or params[0].find('dnew') != -1:
      # Customコード/Documentを新規作成する。コード/ドキュメントのデフォルト作成とindexの更新
      # [1]: コード名
      # [2]: ユーザー名
      target = 'cod'
      if params[0].find('dnew') != -1:
        target = 'doc'
      if (os.path.isfile(PATH + '/custom/' + params[2] + '/' + target + '/index')):
        data = readsearch('custom/' + params[2] + '/' + target + '/index')
        lines = data.split("\n")
        i = 1
        strs = ''
        for check in lines:
          if len(check) > 2:
            strs = strs + check + '\n'
            ops = check.split("\t")
            if ops[1].find(params[1]) != -1:
              result = "Duplicate Title!"
              return [result]
            i = i + 1
        strs = strs + str(i) + '\t' + params[1] + '\n'
        fcreate('custom/' + params[2] + '/' + target + '/index',strs)
        fcreate('custom/' + params[2] + '/' + target + '/' + str(i) + '.c', 'Free Shell Code\n')
        result = 'create ' + params[1] + ' success'
      else:
        fcreate('custom/' + params[2] + '/' + target + '/index', '1\t' + params[1] + '\n')
        fcreate('custom/' + params[2] + '/' + target + '/' + '1.c', 'Free Shell Code\n')
        result = 'create ' + params[1] + ' success'
    else:
      cmd = ''
      if params[0].find('gwordlist') != -1:
        # Global Wordをファイルをより取得し戻り文字列に格納する
        # [1]: ユーザー名
        # [2]: モード
        cmd = 'custom/' + params[1] + '/' + params[2] + '/gword'
      elif params[0].find('pcode') != -1:
        # publicコードを取得し戻す。
        # [1]: publicコードの格納順
        cmd = 'public/' + params[1] + '.c'
      elif params[0].find('ccode') != -1:
        # customコードを取得し戻す。
        # [1]: customコードの格納順
        # [2]: ユーザー名
        cmd = 'custom/' +  params[2] + '/cod/' +  params[1] + '.c'
      elif params[0].find('cdoc') != -1:
        # documentを取得し戻す。
        # [1]: documentコードの格納順
        # [2]: ユーザー名
        cmd = 'custom/' +  params[2] + '/doc/' +  params[1] + '.c'
      elif params[0].find('pans') != -1:
        # publicコードの変換後コードを取得し戻す。
        # [1]: customコードの格納順
        cmd = 'public/' + params[1] + '.a'
      result = readsearch(cmd)
    print 'result: ' + result
    return [result]

if __name__ == '__main__':
    start(PORT, callback_method)

