from flask import Blueprint
from flask import render_template
from flask import request

from .models import Post, Tag


posts = Blueprint('posts', __name__, template_folder='templates')


@posts.route('/')
def index():

    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    posts_list = Post.query.order_by(Post.created.desc())

    pages = posts_list.paginate(page=page, per_page=3)

    return render_template('posts/index.html', pages=pages)


@posts.route('/tags')
def tags_list():
    tags = Tag.query.all()
    return render_template('posts/tags_list.html', tags=tags)


@posts.route('/<pk>')
def post_detail(pk):
    post = Post.query.filter(Post.id == pk).first_or_404()
    tags = post.tags
    return render_template('posts/post_detail.html', post=post, tags=tags)


@posts.route('/tag/<pk>')
def tag_detail(pk):
    tag = Tag.query.filter(Tag.id == pk).first_or_404()
    posts_list = tag.posts.all()
    return render_template('posts/tag_detail.html', tag=tag, posts=posts_list)
