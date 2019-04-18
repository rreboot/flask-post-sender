from flask_security import current_user
from flask import redirect, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_ckeditor import CKEditorField
from flask_admin import form
from config import Config, op
import os
from datetime import datetime
from app.posts.models import Attachment
from app.database import db
from app.vk_post import PostWall, GROUP_ID, API_VERSION, ACCESS_TOKEN  # TODO: replace this!

from flask_admin import Admin

uploads = Config.UPLOADED_PATH
try:
    os.mkdir(uploads)
except OSError:
    pass


class AdminMixin:
    def is_accessible(self):
        if not current_user.is_authenticated or not current_user.is_active:
            return False
        return current_user.has_role('admin') or current_user.has_role('editor')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))

    def _handle_view(self, name, **kwargs):
        if self.is_accessible():
            if current_user.has_role('editor'):
                self.can_delete = False
                self.can_edit = False
            else:
                self.can_delete = True
                self.can_edit = True
        else:
            return redirect(url_for('security.login', next=request.url))


class AdminView(AdminMixin, ModelView):
    pass


class HomeAdminView(AdminMixin, AdminIndexView):
    pass


# Administrative views
class PostView(AdminMixin, ModelView):
    form_columns = ['title',
                    'announce',
                    'description',
                    'pub_date',
                    'published',
                    'is_draft',
                    'file',
                    'tags',
                    'attachments']

    def _handle_view(self, name, **kwargs):
        if self.is_accessible():
            if current_user.has_role('editor'):
                self.can_delete = False
                self.can_edit = False
                self.form_excluded_columns = ['is_draft']
            else:
                self.can_delete = True
                self.can_edit = True
        else:
            return redirect(url_for('security.login', next=request.url))

    form_overrides = {
        'description': CKEditorField,
        'announce': CKEditorField,
    }

    form_extra_fields = {
        'file': form.ImageUploadField('Image',
                                      base_path=uploads,
                                      thumbnail_size=(100, 100, True))
    }

    def on_model_change(self, form, model, is_created):
        path_list = [x.path for x in Attachment.query.filter_by(post_id=model.id)]
        if request.files.get('file'):
            path = op.join(uploads, request.files.get('file').filename)
            if path not in path_list:
                db.session.add(Attachment(path=path, post_id=model.id))
        for link in model.get_imgurls():
            if link not in path_list:
                db.session.add(Attachment(path=link, post_id=model.id))
        path_list = [x.path for x in Attachment.query.filter_by(post_id=model.id)]

        if not model.published and not model.is_draft:
            wp = PostWall(GROUP_ID, ACCESS_TOKEN, API_VERSION)
            pub_time = None
            if model.pub_date is not None:
                pub_time = int(model.pub_date.strftime('%s'))
                s_time = int(wp.get_server_time())
                if (pub_time - s_time) < 100:
                    pub_time = None

            result = wp.post_on_wall(model.assemble_text(), path_list, pub_time, model.id)
            if result == 'ok':
                model.pub_date = datetime.now()
                model.published = True

        return super(PostView, self).on_model_change(form, model, is_created)

    create_template = 'admin/create_post.html'
    edit_template = 'admin/create_post.html'


class TagView(AdminMixin, ModelView):
    form_columns = ['title']


admin = Admin(index_view=HomeAdminView(), template_mode='bootstrap3')
