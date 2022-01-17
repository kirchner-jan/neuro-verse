#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template , request
from flask_ngrok import run_with_ngrok
from anytree.importer import JsonImporter
import numpy as np
import logging
import sys

importer = JsonImporter()
#with open('/content/drive/MyDrive/g_projects/OMEN/stroco/tree_out.json') as f:
with open('tree_out.json') as f:
  root = importer.read(f)

def update_app_data(app_data , splitValue):
  app_data['history'] += splitValue
  return app_data

app_data = {
    "html_title":   "A stroll through the metaverse of stream-of-consciousness neuroscience",
    "root": root,
    "history": root.name + '<br><br>',
    "cnode": root,
    "children_name": [x.name for x in root.children]
}

app = Flask(__name__)
# run_with_ngrok(app)  # Start ngrok when app is run

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', app_data=app_data)

@app.route('/explore/<path:treeloc>', methods=['GET', 'POST'])
def tree_explore(treeloc):
    print(treeloc)
    new_data = app_data.copy()
    path = [int(a) for a in treeloc.split('/') if len(a) > 0] # if len(treeloc) > 9 else [int(treeloc)]
    cNode = root
    history = cNode.name + '<br><br>'
    pathHist = ''
    for choice in path:
        cNode = cNode.children[choice]
        history += '<a href="/explore/'+ pathHist +'">^</a> ' + cNode.name + '<br><br>' if len(pathHist) > 0 else '<a href="/'+ pathHist +'">^</a> ' + cNode.name + '<br><br>'
        pathHist += str(choice) + '/'
    new_data['history'] = history
    s_ratings = np.array([x.s_rating for x in cNode.children])
    g_ratings = np.array([x.g_rating for x in cNode.children])
    t_rating = np.sqrt(s_ratings**2 + g_ratings**2)
    new_data['children_name'] = [x.name for x in cNode.children]
    new_data['children_name'] = [x for _, x in sorted(zip(t_rating, new_data['children_name']))]
    new_data['treeloc'] = treeloc
    return render_template('tree_explore.html', new_data=new_data)

if __name__ == '__main__':
    app.run()
