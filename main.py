from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = '1234567'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body        
        self.user = user
        
class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref = 'user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login' , 'signup', 'blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        error_msg = ""  
        if username != "" and password != "":
            user = User.query.filter_by(username=username).first()
            if not user:
                error_msg = "Username does not exist"
                return render_template('login.html', error_msg=error_msg)
            elif user and user.password == password:
                session['username'] = username
                flash("LOGGED IN")
                return redirect('/newpost')
            elif user and user.password != password:
                error_msg = "Incorrect Password"
                return render_template('login.html', error_msg=error_msg)

        else:
            error_msg = "Username and password cannot be blank"
            return render_template('login.html',error_msg=error_msg)
    else:
        return render_template("login.html")

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username=str.strip(request.form["username"])
        password=str.strip(request.form["password"])
        verify=str.strip(request.form["verify"])
    
        error_msg = ""

        if username != "" and password != "" and verify != "":
            if password != verify:
                error_msg = "Password and Verify password do not match"
                return render_template('signup.html', error_msg=error_msg)

            if len(username) < 3 or len(password) < 3:
                error_msg = "Username and Password should be atleast 3 character long"
                return render_template('signup.html', error_msg=error_msg)

            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                error_msg = "User already exist"
                return render_template('signup.html', error_msg=error_msg)

        else:
            error_msg = "Please enter valid username, password and verify password"
            return render_template('signup.html', error_msg=error_msg)
    else: 
        return render_template('signup.html')

@app.route('/logout', methods = ['GET'])
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users = users)

@app.route('/blog', methods=['GET','POST'])
def blogs():
    if request.method == 'GET':
        user_id = request.args.get('user')
        if user_id != None:
            blogs = Blog.query.filter_by(user_id = user_id).all()
            return render_template('singleUser.html', blogs=blogs)


    individual_blog_page = False
    id = request.args.get('id')
    
    if id == None :
        blogs = Blog.query.order_by(Blog.id.desc()).all()

    else:
        blogs = Blog.query.filter_by(id=id).all()
        individual_blog_page = True
    
    
    return render_template("blog.html", blogs = blogs, individual_blog_page = individual_blog_page)


@app.route('/newpost', methods=['GET','POST'])
def newpost():
    
    if request.method == 'POST':
        title = request.form['title'].strip() 
        body = request.form['body'].strip() 
        error = False
        title_error = ""
        body_error = ""

        if title == "":
            title_error = "Please fill in the title"
            error = True
        if body == "":
            body_error = "Please fill in the body"
            error = True
        if error :
            return render_template("new_post.html", title = title, title_error = title_error, body = body, body_error = body_error)

        user = User.query.filter_by(username=session['username']).first()

        new_blog = Blog(title, body, user)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blog?id='+str(new_blog.id))
    else:
        return render_template("new_post.html")


if __name__ == '__main__':
    app.run()

