from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps


# ***********// Forms //************

# Register Form
class RegisterForm(Form):
    name = StringField("Name Surname",validators=[validators.length(min = 4, max = 25)])
    username = StringField("Username",validators=[validators.length(min = 4, max = 16)])
    email = StringField("Email Adress",validators=[validators.Email(message = "Please enter valid email adress")])
    password = PasswordField("Password",
    validators=[
        validators.data_required(message="Please set a password"),
        validators.equal_to(fieldname="confirm",message="Password doesnt match")
        ])
    confirm = PasswordField("Confirm Password")

# Login Form
class LoginForm(Form):
    username = StringField("Username")
    password = PasswordField("Password")

# Add Article Form

class ArticleForm(Form):
    title = StringField("Title",validators=[validators.length(min=5,max=120)])
    content = TextAreaField("Content",validators=[validators.length(min=10)])







# ***********// Decorators //************

# Login Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "online" in session:
            return f(*args, **kwargs)
        else:
            flash("You need to be logged in to see this page","danger")
            return redirect(url_for("login"))

    return decorated_function








# ***********// App Configs //************

app = Flask(__name__)

app.secret_key = "blog"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


# ***********// Routes and Rendering Functions //************



@app.route("/")
def index():
    
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/article/<string:id>")
def detail(id):
    return "Article Id:" + id

# Register
@app.route("/register", methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.hash(form.password.data)

        cursor = mysql.connection.cursor()
        checksql = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(checksql,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()

        flash("Registeration is successful","success")

        return redirect(url_for("login"))
    else:
        return render_template("register.html", form = form)


# Login
@app.route("/login", methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        passwordEntered = form.password.data

        cursor = mysql.connection.cursor()
        
        checksql = "Select * From users where username = %s"

        result = cursor.execute(checksql,(username,))

        if result > 0:
            data = cursor.fetchone()
            realPassword = data["password"]
            if sha256_crypt.verify(passwordEntered,realPassword):
                flash("You are sucessfully signed in","success")
                session["online"] = True
                session["username"] = username
                return redirect(url_for("index"))
            else:
                flash("Password is not correct","danger")
                return redirect(url_for("login"))
        else:
            flash("User does not exist","danger")
            return redirect(url_for("login"))



    return render_template("login.html",form = form)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))





# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# Add Article
@app.route("/addarticle", methods = ["GET","POST"])
def addArticle():
    form = ArticleForm(request.form)

    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        
        cursor = mysql.connection.cursor()
        checksql = "Insert into articles(title,author,content) VALUES(%s,%s,%s)"
        cursor.execute(checksql,(title,session["username"],content))
        mysql.connection.commit()
        cursor.close()
        flash("Article posted successfully","success")
        return redirect(url_for("dashboard"))







    return render_template("addarticle.html",form = form)


if __name__ == "__main__":
    app.run(debug=True)