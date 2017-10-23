from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import cgi
import datetime
import time

app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz12345@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db=SQLAlchemy(app)
app.secret_key = "mikesblog1234567"


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    author = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='author_id')

def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('index')

@app.before_request
def require_login():
    routes = ['index','userposts','blog','login','signup']
    if request.endpoint not in routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = False
        un_err = ""
        pw_err = ""
        login_err = ""
        if username == "":
            un_err = "Please enter a valid username"
            error = True
        if password == "":
            pw_err = "Please enter a valid password"
            error = True

        if error == True:
            return render_template('login.html',username = username, un_err =  un_err, pw_err = pw_err)
        else:
            user = User.query.filter_by(username=username).first()

            if user and user.password == password:
                session['username'] = username
                flash("Logged in")
                return redirect('/newpost')
            elif not user:
                return render_template('login.html',username = username, un_err = "Username not found")
            elif user and user.password != password:
                return render_template('login.html',username = username, pw_err = "Invalid password")

            else:
                login_err = "Invalid Username or Password"
                return render_template('login.html',username = username, login_err = login_err)

    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        ver_password = request.form['ver_password']
        error = False
        un_err = ""
        pw_err = ""
        login_err = ""
        if username == "":
            un_err = "Please enter a valid username"
            error = True
        if password == "":
            pw_err = "Please enter a valid password"
            error = True
        if password != ver_password:
            pw_err = "Passwords must match"
            error = True

        if error == True:
            return render_template('signup.html',username = username, un_err =  un_err, pw_err = pw_err)
        else:
            ex_user = User.query.filter_by(username=username).first()
            if not ex_user:
                new_user = User(username = username, password = password)
                db.session.add(new_user)
                db.session.commit()

                session['username'] = username
                flash("Sign Up Completed")
                return redirect('/')
            else:
                signup_err = "Username already taken. Please select another"
                return render_template('signup.html',username = username, signup_err = signup_err)

    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        del session['username']
    return redirect('/')

@app.route('/', methods=['GET'])
def index():

    users = User.query.order_by(User.id.desc()).all()
    return render_template('index.html', users = users)

@app.route('/blog', methods=['GET'])
def blog():

    post_id = request.args.get("id")

    if (post_id):
        post_id = cgi.escape(post_id)
        post = Blog.query.get(post_id)
        back = redirect_url()
        delete=""
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user and user.id == post.author:
                delete="delete"


        return render_template('single_post.html', post = post, delete = delete, back = back)
    else:
        posts = Blog.query.order_by(Blog.pub_date.desc()).all()
        return render_template('posts.html', posts = posts)

@app.route('/userposts', methods=['GET'])
def userposts():

    userid = request.args.get("userid")
    user = User.query.get(userid)
    if user:
        userid = cgi.escape(userid)
        posts = Blog.query.filter_by(author = user.id).order_by(Blog.pub_date.desc()).all()

        return render_template('posts.html', posts = posts)
    else:
        return redirect('/blog')

@app.route('/newpost', methods=['GET', 'POST'])
def addnew():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if title == "" or content =="":
            error="Please fill out all fields"
            return redirect('/newpost?error=' + error)

        user = User.query.filter_by(username=session['username']).first()

        new_post = Blog(title = title, body = content, pub_date = datetime.datetime.now(), author = user.id)
        db.session.add(new_post)
        db.session.commit()
        
        return redirect('/blog?id=' + str(new_post.id))
    else:

        error = request.args.get("error")

        if error:
            error = cgi.escape(error, quote=True)
        else:
            error = ''
        return render_template('add_post.html', error = error)

@app.route('/delete', methods=['GET'])
def delete():

    post_id = request.args.get("id")

    if (post_id):
        post_id = cgi.escape(post_id)
        post = Blog.query.get(post_id)
        db.session.delete(post)
        db.session.commit()
        return redirect("/blog")
    else:
        return redirect("/blog")

if __name__ == '__main__':
    app.run()