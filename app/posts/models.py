import re
from datetime import datetime

from app.database import db
from config import op, basedir

post_tags = db.Table('post_tags',
                     db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                     )


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    announce = db.Column(db.Text)
    description = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.now())
    pub_date = db.Column(db.DateTime, nullable=True, default=datetime.now())
    published = db.Column(db.Boolean, default=False)
    is_draft = db.Column(db.Boolean, default=True)
    tags = db.relationship('Tag',
                           secondary=post_tags,
                           backref=db.backref('posts', lazy='dynamic'))
    attachments = db.relationship('Attachment',
                                  cascade='all, delete-orphan',
                                  backref='post')

    def get_imgurls(self):
        pattern = re.compile(r'src\s*=\s*"(.+?)"')
        urls = re.findall(pattern, self.description)
        return [op.join(basedir, url[1:]) for url in urls]

    def assemble_text(self):
        pattern = re.compile(r'<.*?>')
        message = re.sub(pattern, '', self.description)
        tags = ' '.join(['#' + x.title.replace(' ', '_') for x in self.tags])
        return '{}\n{}\n{}'.format(self.title, message, tags)

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.title


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.title


class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(300))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Attachment, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '{}:{}:{}'.format(self.id, self.path, self.post_id)