import os
from flask import render_template, url_for, request
from flask import send_from_directory
from flask_ckeditor import upload_success, upload_fail
from werkzeug.contrib.atom import AtomFeed
from werkzeug.utils import secure_filename

from config import op, basedir
from app.main import bp
from app.posts.models import Post

uploads = op.join(basedir, 'uploads')


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/feed')
def atom_feed():
    feed = AtomFeed("My Blog", feed_url=request.url,
                    url=request.host_url,
                    subtitle="My example blog")
    for post in Post.query.limit(10).all():
        feed.add(post.title, post.announce, content_type='html',
                 id=post.id, updated=post.created, published=post.created,
                 url=url_for('posts.post_detail', pk=post.id))
    return feed.get_response()


@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@bp.route('/uploads/<filename>')
def uploaded_files(filename):
    return send_from_directory(uploads, filename)


@bp.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    unique_filename = secure_filename(f.filename.split('.')[0].lower())
    f.filename = unique_filename + '.' + extension
    f.save(op.join(uploads, f.filename))
    url = url_for('main.uploaded_files', filename=f.filename)
    return upload_success(url=url)


@bp.route('/browse')
def browse():
    files = []
    for r, d, f in os.walk(uploads):
        for file in f:
            files.append(os.path.join(r, file))
    return render_template('browse.html', files=files)
