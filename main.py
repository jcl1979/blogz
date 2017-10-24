from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'spaceballs12345'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer , db.ForeignKey('user.id'))

    def __init__ (self, title, body, author):
        self.title = title
        self.body = body
        self.author = author

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='author')

    def __init__ (self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        bad_pass = ''
        user_err = ''
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        if user and user.password != password:
            bad_pass = 'password incorrect for user!'
        if not user:
            user_err = 'user does not exist!'
        if bad_pass != '' or user_err != '':
            return render_template('login.html', username=username, password=password,
                user=user, bad_pass=bad_pass, user_err=user_err)
        
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        existing_user = User.query.filter_by(username=username).first()
        user_err = ''
        pass_err = ''
        ver_err = ''
        duplicate = ''
        if len(username) <= 3:
            user_err = 'username must be 4 characters or longer!'
        if existing_user:
            duplicate = 'user already exists!'
        if len(password) <= 3:
            pass_err = 'password must be 4 characters or longer!'
        if password != verify:
            ver_err = 'passwords must be the same!'
        if user_err != '' or duplicate != '' or pass_err != '' or ver_err != '':
            return render_template('signup.html', username=username, duplicate=duplicate, password=password, verify=verify,
                user_err=user_err, pass_err=pass_err, ver_err=ver_err)
        else:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
            return redirect('/newpost')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    if request.method == 'POST':
        new_title = request.form['title']
        new_body = request.form['body']
        author = User.query.filter_by(username=session['username']).first()
        title_error = ''
        body_error = ''
        if len(new_title) == 0:
            title_error = 'Please enter a title'
        if len(new_body) == 0:
            body_error = 'Please enter a blog'
        if title_error != '' or body_error != '':
            return render_template('newpost.html', title_error=title_error,
                body_error=body_error, new_title=new_title, new_body=new_body)
        else:
            blog = Blog(new_title, new_body, author)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog?id=' + str(blog.id))
      
    return render_template('/newpost.html')


@app.route('/blog', methods=['POST','GET'])
def blog():
    blog_id = request.args.get('blogid')
    user_id = request.args.get('userid')
    
    if blog_id != None:
        blog = Blog.query.get(blog_id)
        return render_template('individual.html', blog=blog)

    if user_id != None:
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('mainblog.html', title='Blog Posts', blogs=blogs)
    else:  
        blogs = Blog.query.all()
    
    return render_template('mainblog.html', title='Blogs by Users', blogs=blogs)

    
@app.route('/', methods=['POST', 'GET'])
def index():


    users = User.query.all()

    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()
