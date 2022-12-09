from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from sqlalchemy.exc import IntegrityError
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
ckeditor = CKEditor(app)
Bootstrap(app)

# #CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# #CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# #WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    posts = BlogPost.query.all()
    requested_post = None
    for blog_post in posts:
        if blog_post.id == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/edit-post", methods=["GET", "POST"])
def edit_post():
    form = CreatePostForm()
    check = 1
    # Auto-populating the edit fields
    post_id = request.args.get("post_id")
    post_to_edit = BlogPost.query.filter_by(id=post_id).first()
    edit_form = CreatePostForm(
        title=post_to_edit.title,
        subtitle=post_to_edit.subtitle,
        img_url=post_to_edit.img_url,
        author=post_to_edit.author,
        body=post_to_edit.body
    )
    if request.method == "POST":
        # Editing existing form
        try:
            # current_date = datetime.datetime.now()
            post_to_edit.title = form.title.data
            post_to_edit.subtitle = form.subtitle.data
            # post_to_edit.date = current_date.strftime("%B" " " "%#d" " " "%Y")
            post_to_edit.body = form.body.data
            post_to_edit.author = form.author.data
            post_to_edit.img_url = form.img_url.data
            db.session.commit()
            return redirect(url_for("get_all_posts"))
        except IntegrityError:
            pass
    return render_template("make-post.html", check=check, form=edit_form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    check = 0
    form = CreatePostForm()
    try:
        if request.method == "POST":
            current_date = datetime.datetime.now()
            new_edited_post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                date=current_date.strftime("%B" " " "%#d" " " "%Y"),
                body=form.body.data,
                author=form.author.data,
                img_url=form.img_url.data
            )
            db.session.add(new_edited_post)
            db.session.commit()
            return redirect(url_for("get_all_posts"))
    except IntegrityError:
        pass
    return render_template("make-post.html", form=form, check=check)


@app.route("/delete")
def delete_post():
    posts = BlogPost.query.all()
    post_id = request.args.get("post_id")
    for blog_post in posts:
        if blog_post.id == int(post_id):
            selected_post_to_delete = BlogPost.query.filter_by(id=blog_post.id).first()
            db.session.delete(selected_post_to_delete)
            db.session.commit()
        else:
            print("FUCK")
    return redirect(url_for("get_all_posts"))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
