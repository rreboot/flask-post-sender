from flask import Flask
from flask_ckeditor import CKEditor
from .database import db
from config import Config
from flask_security import SQLAlchemyUserDatastore, Security

ckeditor = CKEditor()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    ckeditor.init_app(app)

    with app.test_request_context():
        db.create_all()

    from app.posts.controllers import posts
    app.register_blueprint(posts, url_prefix='/posts')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.admin.controllers import admin, PostView, TagView, AdminView
    admin.init_app(app)

    from .admin.models import User, Role
    from .posts.models import Post, Tag, Attachment
    admin.add_view(PostView(Post, db.session))
    admin.add_view(TagView(Tag, db.session))
    admin.add_view(AdminView(Attachment, db.session))
    admin.add_view(AdminView(User, db.session))
    admin.add_view(AdminView(Role, db.session))

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    return app

#
# admin = Admin(app, index_view=HomeAdminView(), template_mode='bootstrap3')
#
#
# # Add views
# admin.add_view(PostView(Post, db.session))
# admin.add_view(TagView(Tag, db.session))
# admin.add_view(AdminView(Attachment, db.session))
# admin.add_view(AdminView(User, db.session))
# admin.add_view(AdminView(Role, db.session))
#
#
# # Security
