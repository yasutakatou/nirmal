# -*- coding: utf-8 -*-
import subprocess
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

training_docs = []

dvec = []
tags = []
cnt = 0
f = open('./public/index')
line = f.readline()
while line:
  words = []
  lines = line.split("\t")
  tags.append(lines[1].rstrip())
  ret = subprocess.check_output('cat ./public/' + lines[0] + '.c | tr -s " " | sed -e "s/^ //g" -e "s/,//g" | grep -v "^#"', shell=True)
  csvs = ret.split("\n")
  for dat in csvs:
    words.append(dat)
  print ' -- words -- '
  print words
  dvec.append(TaggedDocument(words,tags))
  training_docs.append(dvec[cnt]) 
  cnt = cnt + 1
  line = f.readline()
f.close()

print ' -- tags -- '
print tags

model = Doc2Vec(documents=training_docs, min_count=1, dm=0)

model.save('./doc2vec.model')

