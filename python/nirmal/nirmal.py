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

# ���s�p�X�擾
PATH = os.path.dirname(os.path.abspath(__file__))
print 'PATH: ' + PATH

#�S�s�ǂݍ���
def readsearch(filename):
  f = open(PATH + '/' + filename)
  data = f.read()
  f.close()
  return data

#��t�@�C�������A�܂��͕�������Z�b�g���ꂽ��t�@�C���ɏ�������
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
        # POST�����p�����[�^��ϐ��Ɋi�[�B�ϐ��͈ȉ�
        # ctrl: �����ނ��w��
        # user: ���[�U�[�����w��
        # typa: ���[�h(Code / Document)���w��
        # typb: ���[�h�z���̉��𑀍삷�邩���w��
        # code: POST�����R�[�h��f�[�^���w��
        for key in form.keys():
          value = form.getvalue(key,'')
          exec '%s = """%s"""' % (key,value)
        # �u���E�U�ɕԂ��������result�ɂ܂Ƃ߂�
        result = ctrl + ' success'
        if (ctrl == 'repo'):
          # ���|�W�g���ɃR�~�b�g���ăt�@�C���쐬�B���̃}�X�^�[����t�ɉ����B
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
          # Global Word���R�~�b�g���ăt�@�C���쐬�B���t�@�C���͍폜
          os.remove(PATH + '/custom/' + user + '/' + typa + '/gword')
          fcreate('custom/' + user + '/' + typa + '/gword', code)
        elif (ctrl == 'comren'):
          # �R�[�h����ύX�Bchgs�Ɋi�[���C���f�b�N�X�œ������O�̂��̂�u�������ăt�@�C���쐬�B
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
          # POST���ꂽ�R�[�h��Doc2Vec��public�̃R�[�h���|�W�g������ގ���T���A���ʂ�߂�l�ŕԂ��B
          # ���̕��������߂�l��javascript�ŉ��H����B�ގ����̊w�K�͕ʓr���{���K�v(train.py)
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
          # POST���ꂽ�R�[�h����s�����s���Č��ʂ�߂�l�ŕԂ��B�G���[�̏ꍇ�͋�B
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
    # �u���E�U�ɕԂ��������result�ɂ܂Ƃ߂�
    result = ''
    strs = ''
    # �p�����[�^�𕪊����A���C������
    params = query.split("=")
    if params[0].find('comcode') != -1:
      # ���݂̃}�X�^�[�����ݓ�����t���ă��l�[�����ACommit���ꂽ�t�@�C�����}�X�^�[���Ƀ��l�[������
      # [1]: ���[�U�[��
      # [2]: ���[�h(Code / Document)
      # [3]: id=comX:Y��X�B���|�W�g���i�[��������
      daystr = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
      os.rename(PATH + '/custom/' + params[1] + '/' + params[2] + '/' + params[3].split(".")[0] + '.c', PATH + '/custom/' + params[1] + '/' + params[2] + '/' + params[3].split(".")[0] + '.' + daystr)
      os.rename(PATH + '/custom/' + params[1] + '/' + params[2] + '/' + params[3], PATH + '/custom/' + params[1] + '/' + params[2] + '/' + params[3].split(".")[0] + '.c')
      result = 'Commit success'
    elif params[0].find('delcode') != -1:
      # �u�����`�������ꍇ�͂��̂܂܏����B�}�X�^�[�������ꍇ�̓u�����`������΍ŐV�̃u�����`���}�X�^�[�ɏ��i�B�u�����`��������΃C���f�b�N�X����������B
      # [1]: ���[�U�[��
      # [2]: ���[�h(Code / Document)
      # [3]: id=comX:Y�B���|�W�g���i�[���ƃ��|�W�g����������
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
      # ���|�W�g�����X�g��ʂ�HTML�𐶐����Ė߂��B���j���[�{�^�����܂߂�HTML�^�O����������̂ł��̂܂ܕ\���B
      # [1]: ���[�U�[��
      # [2]: ���[�h(Code / Document)
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
      # public/custom/document�̃C���f�b�N�X���擾���߂��B
      # [1]: ���[�h(Code / Document)
      # [2]: ���[�U�[��
      if params[1].find('public') != -1:
        result = readsearch('public/index')
      elif params[1].find('customc') != -1:
        result = readsearch('custom/' + params[2] + '/cod/index')
      else:
        result = readsearch('custom/' + params[2] + '/doc/index')
    elif params[0].find('auth') != -1:
      # ���[�U�|�̃t�H���_�����邩�ǂ����ŔF�؂���B�Ȃ����fail��Ԃ��B
      # [1]: ���[�U�[��
      if (os.path.exists(PATH + '/custom/' + params[1])):
        result = 'true'
      else:
        result = 'fail'
    elif params[0].find('cnew') != -1 or params[0].find('dnew') != -1:
      # Custom�R�[�h/Document��V�K�쐬����B�R�[�h/�h�L�������g�̃f�t�H���g�쐬��index�̍X�V
      # [1]: �R�[�h��
      # [2]: ���[�U�[��
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
        # Global Word���t�@�C�������擾���߂蕶����Ɋi�[����
        # [1]: ���[�U�[��
        # [2]: ���[�h
        cmd = 'custom/' + params[1] + '/' + params[2] + '/gword'
      elif params[0].find('pcode') != -1:
        # public�R�[�h���擾���߂��B
        # [1]: public�R�[�h�̊i�[��
        cmd = 'public/' + params[1] + '.c'
      elif params[0].find('ccode') != -1:
        # custom�R�[�h���擾���߂��B
        # [1]: custom�R�[�h�̊i�[��
        # [2]: ���[�U�[��
        cmd = 'custom/' +  params[2] + '/cod/' +  params[1] + '.c'
      elif params[0].find('cdoc') != -1:
        # document���擾���߂��B
        # [1]: document�R�[�h�̊i�[��
        # [2]: ���[�U�[��
        cmd = 'custom/' +  params[2] + '/doc/' +  params[1] + '.c'
      elif params[0].find('pans') != -1:
        # public�R�[�h�̕ϊ���R�[�h���擾���߂��B
        # [1]: custom�R�[�h�̊i�[��
        cmd = 'public/' + params[1] + '.a'
      result = readsearch(cmd)
    print 'result: ' + result
    return [result]

if __name__ == '__main__':
    start(PORT, callback_method)

