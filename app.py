#!/usr/bin/env python
import os
from datetime import datetime
import yaml
try:
    import misaka
    markdown_html = misaka.html
except ImportError:
    import markdown
    markdown_html = markdown.markdown

from flask import Flask, render_template, abort, send_from_directory


PORT = 45061
POSTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICS_DIR = os.path.join(POSTS_DIR, 'pics')

app = Flask(__name__)


@app.route('/')
def index():
    dates = [fn.rsplit('.', 1)[0] for fn in os.listdir(POSTS_DIR)]
    dates.extend([fn.split()[0] for fn in os.listdir(PICS_DIR)])
    dates = list(set(dates))
    dates.sort()

    posts = []
    for date in dates:
        post = load_post(date)
        if not post:
            continue
        posts.append({k: post[k] for k in ['date', 'title', 'pics']})
    return render_template('index.html', posts=posts)


@app.route('/<date>/')
def post(date):
    post = load_post(date)
    if not post:
        abort(404)
    return render_template(post['template'], post=post)


@app.route('/pic/<fname>')
def pic(fname):
    return send_from_directory(PICS_DIR, fname)


@app.template_filter('markdown')
def markdown_filter(s):
    return markdown_html(s)


def load_post(date):
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return

    pics = load_pics(date)
    post = {}
    path = os.path.join(POSTS_DIR, '%s.yml' % date)
    if os.path.isfile(path):
        with open(path) as f:
            post = yaml.load(f)

    post.setdefault('date', date)
    post.setdefault('title', str(date))
    post.setdefault('tags', [])
    post.setdefault('template', 'post.html')
    post.setdefault('pics', pics)
    post.setdefault('body', '')
    return post


def load_pics(date):
    fnames = os.listdir(PICS_DIR)
    fnames.sort()
    date = str(date)
    ret = []
    for fname in fnames:
        if fname.startswith(date):
            ret.append(fname)
    return ret



if __name__ == "__main__":
    app.run(port=PORT, debug=True)
