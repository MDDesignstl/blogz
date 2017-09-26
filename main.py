from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import cgi
import datetime
import time

app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:bab12345@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db=SQLAlchemy(app)



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

@app.route('/')
def index():

    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def blog():

    post_id = request.args.get("id")

    if (post_id):
        post_id = cgi.escape(post_id)
        post = Blog.query.get(post_id)
        return render_template('single_post.html', post = post)
    else:
        posts = Blog.query.order_by(Blog.pub_date.desc()).all()
        return render_template('posts.html', posts = posts)

@app.route('/newpost', methods=['GET', 'POST'])
def addnew():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if title == "" or content =="":
            error="Please fill out all fields"
            return redirect('/newpost?error=' + error)
        

        new_post = Blog(title = title, body = content, pub_date = datetime.datetime.now())
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