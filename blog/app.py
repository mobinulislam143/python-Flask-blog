from flask import Flask, render_template,url_for, request, redirect,session, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key= '9e04ba96d90d49729b314b58bf1f7412'
UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


with open('data.json', 'r') as c:
    params = json.load(c)["params"]

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@127.0.0.1/blogcode"

db = SQLAlchemy(app)

class contacts(db.Model):
    # sno, name, emai, mobile, mes, date
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),  nullable=False)
    email = db.Column(db.String(30), nullable=False)
    mobile = db.Column(db.String(12),  nullable=False)
    msg = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(12), nullable=True)
class blogpost(db.Model):
    # sno, title, slug, content, date, img_file
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80),  nullable=False)
    slug = db.Column(db.String(20),  nullable=False)
    content = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(20), nullable=True)

@app.route('/delete/<string:sno>', methods=["GET", "POST"])
def delete(sno):
    if ('user' in session and session['user'] == params["admin_email"]):
        post = blogpost.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/adminlogin")

    

@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params["admin_email"]):
        if request.method == 'POST':
            title = request.form.get('title')
            slug = request.form.get('slug') 
            content = request.form.get('content')
            date = datetime.now()
            img_file = request.files('img_file')

            if sno == '0':
                post = blogpost(title=title, slug=slug, content=content, date=date, img_file=img_file)
                db.session.add(post)
                db.session.commit()
      
        
            else:
                post = blogpost.query.filter_by(sno=sno).first()
                post.title = title
                post.slug = slug
                post.img_file = img_file
                post.content = content
                post.date = date
                db.session.commit()
                return redirect("/edit/"+sno)
        post = blogpost.query.filter_by(sno=sno).first()
        return render_template('edit.html',post=post,sno=sno, params=params)




@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        fname = request.form.get('fname')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        msg = request.form.get('msg')
        entry = contacts(name=fname, date= datetime.now(), mobile=mobile, email=email, msg=msg)
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html')



@app.route('/post/<string:post_slug>',  methods=["GET"])
def post_route(post_slug):
    post = blogpost.query.filter_by(slug=post_slug).first()
    return render_template('post.html', post=post, params=params)

@app.route('/login')
def login():
    return render_template('registration.html')

@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    if ('user' in session and session['user'] == params["admin_email"]):
        posts = blogpost.query.all()
        return render_template('admin.html', posts=posts, params=params)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get("password")
        if (email == params["admin_email"] and password == params["admin_pass"]):
            session['user'] = email
            posts = blogpost.query.all()
            return render_template("admin.html", params=params, posts=posts)
    else:
        return render_template('registration.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/')
@app.route('/home')
def home():
    posts = blogpost.query.filter_by().all()
    return render_template('index.html', posts=posts)



if __name__ == "__main__":
    app.run(debug=True)
