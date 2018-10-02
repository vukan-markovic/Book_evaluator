# import libraries
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from flask_session import Session
from flask_sslify import SSLify
from passlib.apps import custom_app_context as pwd_context
from helpers import *
import datetime
import requests
import random
import re
import os

# configure application
app = Flask(__name__)
mail = Mail(app)

# redirect all http requests to https for secure connections
if 'DYNO' in os.environ:
    sslify = SSLify(app)

# set the secret key to use sessions
app.secret_key = os.urandom(24)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = 10800
app.config["SESSION_COOKIE_HTTPONLY"] = False
app.config["SESSION_COOKIE_SECURE"] = True
Session(app)
       
# configure parameters for sending welcome email to users after registration
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'booktadingclub@gmail.com'
app.config['MAIL_PASSWORD'] = 'PASSWORD_GOES_HERE'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# configure CS50 Library to use SQLite database
database = SQL("sqlite:///bookEvaluator.db")

# index route
@app.route("/")
def index():

    # return rendered index.html page with random books from Google Books API
    return render_template("index.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                            random.choice('abcdefghijklmnopqrstuvwxzy') +
                            "&maxResults=40&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json())


# about route
@app.route("/about")
def about():

    # return rendered about.html page
    return render_template("about.html")


# blog route
@app.route("/blog")
def blog():

    # query database to get all posts
    posts = database.execute("SELECT * FROM posts")

    # empty list that will hold users that posted posts
    usersPosts = list()

    # query database to get users that posted posts and add them to list
    for post in posts:
        user = database.execute("SELECT * FROM users WHERE id = :id", id = post["user_id"])
        usersPosts.append({"id": post["id"], "title": post["title"], "username": user[0]["username"]})

    # return rendered blog.html page with all posts
    return render_template("blog.html", posts = usersPosts)


# search route
@app.route("/search", methods = ["POST", "GET"])
def search():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure title of book was submitted
        if not request.form.get("title"):
            return apology("title")

        # if user provided author of the book
        if request.form.get("author"):
            """
            return rendered result.html page with books from Google Books API written by the provided author that match
            search results
            """
            return render_template("searchResults.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                               request.form.get("title") + "+inauthor:" + request.form.get("author") +
                               "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json())

        # if user provided publisher of the book
        if request.form.get("publisher"):
            """
            return rendered result.html page with books from Google Books API published by provided publisher that match search
            results
            """
            return render_template("searchResults.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                               request.form.get("title") + "+inpublisher:" + request.form.get("publisher") +
                               "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json())

        # if user provided author and publisher of the book
        if request.form.get("author") and request.form.get("publisher"):
            """
            return rendered result.html page with books from Google Books API written by provided author and published by provided
            publisher that match search results
            """
            return render_template("searchResults.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                               request.form.get("title") + "+inauthor:" + request.form.get("author") + "+inpublisher:" +
                               request.form.get("publisher") + "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json())

        # return rendered result.html page with books from Google Books API that match search results
        return render_template("searchResults.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                               request.form.get("title") + "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json())


    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # return rendered search.html page
        return render_template("search.html")


# profile route, it is necessary that the user be logged in
@app.route("/profile")
@login_required
def profile():

    # query database to get user that is logged in to show his informations on his profile page
    user = database.execute("SELECT * FROM users WHERE id = :id", id = session["user_id"])

    # query database to get all user's readed books to show them on his profile page
    books = database.execute("SELECT * FROM books WHERE user_id = :user_id", user_id = session["user_id"])

    # empty list which will hold all books that user read
    readedBooks = list()

    # get all books from Google Books API that user read and add them to list
    for book in books:
        readedBooks.append(requests.get("https://www.googleapis.com/books/v1/volumes?q=" + book["book_id"] +
                                        "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json()["items"][0])

    # query database to get all user's comments to show them on his profile page
    comments = database.execute("SELECT * FROM comments WHERE user_id = :user_id", user_id = session["user_id"])

    # empty list which will hold all user's comments
    usersComments = list()

    # get all books from Google Books API that user comment and add them to list
    for comment in comments:
        book = requests.get("https://www.googleapis.com/books/v1/volumes?q=" + comment["book_id"] +
                            "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json()
        usersComments.append({"id": comment["id"], "comment": comment["comment"], "dateOfPublish": comment["dateOfPublish"],
                              "book": book["items"][0]})

    # query database to get all user's grades to show them on his profile page
    grades = database.execute("SELECT * FROM grades WHERE user_id = :user_id", user_id = session["user_id"])

    # empty list which will hold all user's grade
    usersGrades = list()

    # get all books from Google Books API that user grade and add them to list
    for grade in grades:
        book = requests.get("https://www.googleapis.com/books/v1/volumes?q=" + grade["book_id"] +
                            "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json()
        usersGrades.append({"id": grade["id"], "grade": grade["grade"], "dateOfEvaluation": grade["dateOfEvaluation"],
                            "book": book["items"][0]})

    # query database to get all user's posts to show them on his profile page
    posts = database.execute("SELECT * FROM posts WHERE user_id = :user_id", user_id = session["user_id"])

    # return rendered profile.html page with user that is logged in and with user's readed books, comments, grades and posts
    return render_template("profile.html", user = user[0], books = readedBooks, comments = usersComments, grades = usersGrades,
                            posts = posts)


# book details route
@app.route("/bookDetails/<book_id>")
def bookDetails(book_id):

    # query database to get all readings for this book
    books = database.execute("SELECT * FROM books WHERE book_id = :book_id", book_id = book_id)

    # query database to get all grades for this book
    grades = database.execute("SELECT * FROM grades WHERE book_id = :book_id", book_id = book_id)

    # query database to get all comments for this book
    comments = database.execute("SELECT * FROM comments WHERE book_id = :book_id", book_id = book_id)

    # empty list that will hold all users that posted comments about this book
    usersComments = list()

    # query database to get all users that posted comments and add them to list
    for comment in comments:
        user = database.execute("SELECT * FROM users WHERE id = :id", id = comment["user_id"])
        if user:
            usersComments.append({"id": comment["id"], "comment": comment["comment"], "dateOfPublish": comment["dateOfPublish"],
                                  "username": user[0]["username"], "user_id": comment["user_id"]})

    # empty list that will hold all users that posted grades about this book
    usersGrades = list()

    # query database to get all users that posted grades and add them to list
    for grade in grades:
        user = database.execute("SELECT * FROM users WHERE id = :id", id = grade["user_id"])
        if user:
            usersGrades.append({"id": grade["id"], "grade": grade["grade"], "dateOfEvaluation": grade["dateOfEvaluation"],
                                "username": user[0]["username"], "user_id": grade["user_id"]})

    # count number of readings for this book
    if len(books) > 0:
        numberOfReadings = len(books)
    else:
        numberOfReadings = 0

    # count average grade for this book
    gradesSum = 0

    for grade in grades:
        gradesSum += grade["grade"]

    if len(grades) > 0:
        averageGrade = gradesSum / len(grades)
    else:
        averageGrade = 0
    
    graded = False
    readed = False
    
    # if user is logged in
    if session.get("user_id") != None:
        
        # check if user already graded this book
        for grade in grades:
            if grade["user_id"] == session["user_id"] and grade["book_id"] == book_id:
                graded = True
                break

        # check if user already add this book to diary
        for book in books:
            if book["book_id"] == book_id and book["user_id"] == session["user_id"]:
                readed = True
                break

    # get book from Google Books API that user choose from home page
    book = requests.get("https://www.googleapis.com/books/v1/volumes?q=" + book_id + "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json()

    """
    return rendered bookDetails.html page with book from Google Books API that user choose from home page and with number of
    users that read that book, average grade of that book and all comments and grades for that book
    """
    return render_template("bookDetails.html", book = book["items"][0], numberOfReadings = numberOfReadings,
                            averageGrade = averageGrade, grades = usersGrades, comments = usersComments, graded = graded,
                            readed = readed)


# add comment route, it is necessary that the user be logged in
@app.route("/addComment/<book_id>", methods = ["GET", "POST"])
@login_required
def addComment(book_id):

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure that comment was submitted
        if not request.form.get("comment"):
            return apology("comment")

        # query database for adding new comment about the book
        database.execute("""INSERT INTO comments (comment, dateOfPublish, user_id, book_id)
                            VALUES(:comment, :dateOfPublish, :user_id, :book_id)""", comment = request.form.get("comment"),
                            dateOfPublish = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id = session["user_id"],
                            book_id = book_id)

        # display flash message
        flash("Comment added!")

        # redirect user to book details page
        return redirect(url_for("bookDetails", book_id = book_id))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # return rendered addComment.html page with book id
        return render_template("addComment.html", book_id = book_id)


# update comment route, it is necessary that the user be logged in
@app.route("/updateComment/<int:comment_id>", methods = ["POST", "GET"])
@login_required
def updateComment(comment_id):

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure that updated comment was submitted
        if not request.form.get("updatedComment"):
            return apology("updatedComment")

        # query database for updating user's comment about the book
        database.execute("UPDATE comments SET comment = :comment, dateOfPublish = :dateOfPublish WHERE id = :id",
                          comment = request.form.get("updatedComment"),
                          dateOfPublish = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id = comment_id)

        # display flash message
        flash("Comment is updated!")

        # redirect user to his profile page
        return redirect(url_for("profile"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # query database to get user's comment about the book
        comment = database.execute("SELECT * FROM comments WHERE id = :id", id = comment_id)

        # return rendered updateComment.html page with comment which user choose update
        return render_template("updateComment.html", comment = comment[0])


# delete comment route, it is necessary that the user be logged in
@app.route("/deleteComment/<int:comment_id>", methods = ["GET", "POST"])
@login_required
def deleteComment(comment_id):

    # query database for deleting user comment about the book
    database.execute("DELETE FROM comments WHERE id = :id", id = comment_id)

    # display flash message
    flash("Comment deleted!")

    # redirect user to his profile page
    return redirect(url_for("profile"))


# add grade route, it is necessary that the user be logged in
@app.route("/addGrade/<book_id>", methods = ["GET", "POST"])
@login_required
def addGrade(book_id):

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure that grade was submitted
        if not request.form.get("grade"):
            return apology("grade")

        # query database for adding new grade about the book
        database.execute("""INSERT INTO grades (grade, dateOfEvaluation, user_id, book_id)
                            VALUES(:grade, :dateOfEvaluation, :user_id, :book_id)""", grade = int(request.form.get("grade")),
                            dateOfEvaluation = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id = session["user_id"],
                            book_id = book_id)

        # display flash message
        flash("Grade added!")

        # redirect user to book details page
        return redirect(url_for("bookDetails", book_id = book_id))


    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # return rendered addGrade.html page with book id
        return render_template("addGrade.html", book_id = book_id)


# update grade route, it is necessary that the user be logged in
@app.route("/updateGrade/<int:grade_id>", methods = ["POST", "GET"])
@login_required
def updateGrade(grade_id):

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure that new grade was submitted
        if not request.form.get("updatedGrade"):
            return apology("grade")

        # query database for updating user's grade about the book
        database.execute("UPDATE grades SET grade = :grade, dateOfEvaluation = :dateOfEvaluation WHERE id = :id",
                         grade = request.form.get("updatedGrade"),
                         dateOfEvaluation = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id = grade_id)

        # display flash message
        flash("Grade is updated!")

        # redirect user to his profile page
        return redirect(url_for("profile"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # query database to get user's grade about the book
        grade = database.execute("SELECT * FROM grades WHERE id = :id", id = grade_id)

        # return rendered updateGrade.html page with grade which user choose to update
        return render_template("updateGrade.html", grade = grade[0])


# delete grade route, it is necessary that the user be logged in
@app.route("/deleteGrade/<int:grade_id>", methods = ["GET", "POST"])
@login_required
def deleteGrade(grade_id):

    # query database for deleting user grade
    database.execute("DELETE FROM grades WHERE id = :id", id = grade_id)

    # display flash message
    flash("Grade deleted!")

    # redirect user to his profile page
    return redirect(url_for("profile"))


# post details route
@app.route("/postDetails/<int:post_id>")
def postDetails(post_id):

    # query database to get post that user choose from blog page
    post = database.execute("SELECT * FROM posts WHERE id = :id", id = post_id)

    # query database to get user that published post
    user = database.execute("SELECT * FROM users WHERE id = :id", id = post[0]["user_id"])

    # return rendered postDetails.html page with post and the user which one published that post
    return render_template("postDetails.html", post = post[0], user = user[0])


# publish route, it is necessary that the user be logged in
@app.route("/publish", methods = ["POST", "GET"])
@login_required
def publish():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure that title of the post was submitted
        if not request.form.get("title"):
            return apology("title")

        # ensure that content of the post was submitted
        if not request.form.get("content"):
            return apology("content")

        # query database for adding new post to blog
        database.execute("""INSERT INTO posts (title, content, dateOfPublish, user_id)
                            VALUES(:title, :content, :dateOfPublish, :user_id)""", title = request.form.get("title"),
                            content = request.form.get("content"),
                            dateOfPublish = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id = session["user_id"])

        # display flash message
        flash("Post is published!")

        # redirect user to blog page
        return redirect(url_for("blog"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # return rendered publish.html page
        return render_template("publish.html")


# update post route, it is necessary that the user be logged in
@app.route("/updatePost/<int:post_id>", methods = ["POST", "GET"])
@login_required
def updatePost(post_id):

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure that new title of post was submitted
        if not request.form.get("updatedTitle"):
            return apology("title")

        # ensure that new content of post was submitted
        if not request.form.get("updatedContent"):
            return apology("content")

        # query database for updating user's post
        database.execute("UPDATE posts SET title = :title, content = :content, dateOfPublish = :dateOfPublish WHERE id = :id",
                          title = request.form.get("updatedTitle"), content = request.form.get("updatedContent"),
                          dateOfPublish = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id = post_id)

        # display flash message
        flash("Post is updated!")

        # redirect user to his profile page
        return redirect(url_for("profile"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # query database to get user's post
        post = database.execute("SELECT * FROM posts WHERE id = :id", id = post_id)

        # return rendered updatePost.html page with post that user choose to update
        return render_template("updatePost.html", post = post[0])


# delete post route, it is necessary that the user be logged in
@app.route("/deletePost/<int:post_id>", methods = ["GET", "POST"])
@login_required
def deletePost(post_id):

    # query database for deleting user's post
    database.execute("DELETE FROM posts WHERE id = :id", id = post_id)

    # display flash message
    flash("Post deleted!")

    # redirect user to his profile page
    return redirect(url_for("profile"))


# add book route, it is necessary that the user be logged in
@app.route("/addBook/<book_id>", methods = ["POST", "GET"])
@login_required
def addBook(book_id):

    # query database for adding new book to user diary
    database.execute("INSERT INTO books (book_id, user_id) VALUES(:book_id, :user_id)", book_id = book_id,
                      user_id = session["user_id"])

    # display flash message
    flash("Book is added to your diary!")

    # redirect user to book details page
    return redirect(url_for("bookDetails", book_id = book_id))


# delete book route, it is necessary that the user be logged in
@app.route("/deleteBook/<book_id>", methods = ["GET", "POST"])
@login_required
def deleteBook(book_id):

    # query database for deleting user's book from his diary
    database.execute("DELETE FROM books WHERE book_id = :book_id", book_id = book_id)

    # display flash message
    flash("Book deleted!")

    # redirect user to his profile page
    return redirect(url_for("profile"))


# register route
@app.route("/register", methods = ["GET", "POST"])
@logged
def register():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure that username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure that username is valid
        if not re.match(r'^(?=.{2,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$', request.form.get("username")):
            return apology("must provide valid username")

        # ensure that first name was submitted
        if not request.form.get("firstName"):
            return apology("must provide first name")

        # ensure that first name is valid
        if not re.match(r'^(?=.{2,20}$)(?![_.])(?!.*[_.]{2})[A-Za-z]+(?<![_.])$', request.form.get("firstName")):
            return apology("must provide valid first name")

        # ensure that last name was submitted
        if not request.form.get("lastName"):
            return apology("must provide last name")

        # ensure that last name is valid
        if not re.match(r'^(?=.{2,20}$)(?![_.])(?!.*[_.]{2})[A-Za-z]+(?<![_.])$', request.form.get("lastName")):
            return apology("must provide valid last name")

         # ensure that email was submitted
        if not request.form.get("email"):
            return apology("must provide email")

        # ensure that email is without harmful characters like ' or ;
        if '/''' in request.form.get("email") or ';' in request.form.get("email"):
            return apology("don't use characters like ' or ; for email")

        # ensure that password was submitted
        if not request.form.get("password"):
            return apology("must provide password")

        # ensure that password is valid
        if not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}', request.form.get("password")):
            return apology("must provide valid password")

        # ensure that password was confirmed
        if not request.form.get("confirmPassword"):
            return apology("must confirm password")

        # ensure that passwords matched
        if request.form.get("password") != request.form.get("confirmPassword"):
            return apology("passwords doesn't match")

        # query database for inserting (register) new user
        users = database.execute("""INSERT INTO users (username, hash, firstName, lastName, email)
                                    VALUES(:username, :hash, :firstName, :lastName, :email)""",
                                    username = request.form.get("username"), hash = pwd_context.hash(request.form.get("password")),
                                    firstName = request.form.get("firstName"),
                                    lastName = request.form.get("lastName"), email = request.form.get("email"))

        # ensure that username or email does not exist already, username and email must be unique
        if not users:
            return apology("username or email already exist")

        # remember which user has logged in (registered)
        users = database.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))
        session["user_id"] = users[0]["id"]

        # display flash message
        flash("Registered!")

        """
        send user welcome email after registration
        define title of the email, sender and recipients
        """
        msg = Message('Thank you for registration', sender = 'booktadingclub@gmail.com', recipients = [request.form.get("email")])
        
        # define content of the email
        msg.body = """Hello and thank you for join us! We hope you enjoy at our site where you can search, read, comment and grade
        your favourite books. Have fun!"""
        
        # send email
        mail.send(msg)
        
        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # return rendered register.html page
        return render_template("register.html")


# login route
@app.route("/login", methods = ["GET", "POST"])
@logged
def login():

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email")

        # ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password")

        # ensure password is valid
        if not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}', request.form.get("password")):
            return apology("must provide valid password")

        # query database for getting user email
        users = database.execute("SELECT * FROM users WHERE email = :email", email = request.form.get("email"))

        # ensure email doesn't exists and password is correct, email must be unique
        if len(users) != 1 or not pwd_context.verify(request.form.get("password"), users[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = users[0]["id"]

        # if user is admin, rember his email to enable him additional opportunities
        if request.form.get("email") == "vukan.markovic97@gmail.com":
            session["email"] = request.form.get("email")

        # display flash message
        flash("Logged in!")

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # return rendered login.html page
        return render_template("login.html")


# logout route
@app.route("/logout")
def logout():

    # forget any user_id
    session.clear()

    # display flash message
    flash("Logged out!")

    # redirect user to login page
    return redirect(url_for("login"))


# change password route, it is necessary that the user be logged in
@app.route("/changePassword", methods = ["GET", "POST"])
@login_required
def changePassword():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure that new password was submitted
        if not request.form.get("newPassword"):
            return apology("must provide new password")

        # ensure that new password is valid
        if not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}', request.form.get("newPassword")):
            return apology("""must provide valid password""")

        # update user password to new password
        database.execute("UPDATE users SET hash = :hash WHERE id = :id", hash = pwd_context.hash(request.form.get("newPassword")),
                          id = session["user_id"])

        # display flash message
        flash("Password changed!")

        # redirect user to his profile page
        return redirect(url_for("profile"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # return rendered changePassword.html page
        return render_template("changePassword.html")


# change username route, it is necessary that the user be logged in
@app.route("/changeUsername", methods = ["GET", "POST"])
@login_required
def changeUsername():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure that new username was submitted
        if not request.form.get("newUsername"):
            return apology("must provide new username")

        # ensure that new username is valid
        if not re.match(r'^(?=.{2,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$', request.form.get("newUsername")):
            return apology("must provide valid username")

        # update user username to new username
        users = database.execute("UPDATE users SET username = :username WHERE id = :id", username = request.form.get("newUsername")
                                  , id = session["user_id"])

        # ensure username does not exist already, username must be unique
        if not users:
            return apology("username already exist")

        # display flash message
        flash("Username changed!")

        # redirect user to his profile page
        return redirect(url_for("profile"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # return rendered changeUsername.html page
        return render_template("changeUsername.html")


# change profile picture route, it is necessary that the user be logged in
@app.route("/changeProfilePicture", methods = ["POST", "GET"])
@login_required
def changeProfilePicture():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure that url of new profile picture was submitted
        if not request.form.get("profilePicture"):
            return apology("profile picture")

        # query database for updating user profile picture
        database.execute("UPDATE users SET profilePicture = :profilePicture WHERE id=:id",
                    profilePicture = request.form.get("profilePicture"), id=session["user_id"])

        # display flash message
        flash("Profile pictue is changed!")

        # redirect user to his profile page
        return redirect(url_for("profile"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # return rendered changeProfilePicture.html page
        return render_template("changeProfilePicture.html")


# change email route, it is necessary that the user be logged in
@app.route("/changeEmail", methods = ["GET", "POST"])
@login_required
def changeEmail():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure that new email was submitted
        if not request.form.get("newEmail"):
            return apology("must provide new email")

        # ensure that new email is without harmful characters like ' or ;
        if '/''' in request.form.get("newEmail")  or ';' in request.form.get("newEmail"):
            return apology("Don't use characters like ' or ; for email")

        # update user email to new email
        users = database.execute("UPDATE users SET email = :email WHERE id = :id", email = request.form.get("newEmail")
                                  , id = session["user_id"])

        # ensure that new email does not exist already, email must be unique
        if not users:
            return apology("email already exist")

        # display flash message
        flash("Email changed!")

        # redirect user to his profile page
        return redirect(url_for("profile"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:

        # return rendered changeEmail.html page
        return render_template("changeEmail.html")

# user route
@app.route("/user/<username>")
def user(username):

    # query database to get user to show his information to another user
    user = database.execute("SELECT * FROM users WHERE username = :username", username = username)

    # query database to get all user's readed books to show them to another user
    books = database.execute("SELECT * FROM books WHERE user_id = :user_id", user_id = user[0]["id"])

    # empty list which will hold all books that user read
    readedBooks = list()

    # get all books from Google Books API that user read and add them to list
    for book in books:
        readedBooks.append(requests.get("https://www.googleapis.com/books/v1/volumes?q=" + book["book_id"] + 
                           "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json()["items"][0])

    # query database to get all user's comments to show them to another user
    comments = database.execute("SELECT * FROM comments WHERE user_id = :user_id", user_id = user[0]["id"])

    # empty list which will hold all user's comments
    usersComments = list()

    # get all books from Google Books API that user read and add them to list
    for comment in comments:
        book = requests.get("https://www.googleapis.com/books/v1/volumes?q=" + comment["book_id"] +
                            "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json()
        usersComments.append({"id": comment["id"], "comment": comment["comment"], "dateOfPublish": comment["dateOfPublish"], 
                              "book": book["items"][0]})

    # query database to get all user's grades to show them to another user
    grades = database.execute("SELECT * FROM grades WHERE user_id = :user_id", user_id = user[0]["id"])

    # empty list which will hold books that user grade
    usersGrades = list()

    # get all books from Google Books API that user read and add them to list
    for grade in grades:
        book = requests.get("https://www.googleapis.com/books/v1/volumes?q=" + grade["book_id"] +
                            "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json()
        usersGrades.append({"id": grade["id"], "grade": grade["grade"], "dateOfEvaluation": grade["dateOfEvaluation"], 
                            "book": book["items"][0]})

    # query database to get user's posts to show them to another user
    posts = database.execute("SELECT * FROM posts WHERE user_id = :user_id", user_id = user[0]["id"])

    # return rendered user.html page with user and with all user's readed books, comments, grades and posts
    return render_template("user.html", user = user[0], books = readedBooks, comments = usersComments, grades = usersGrades,
                            posts = posts)


# users route, this route can only access admin to view all registered users
@app.route("/users")
@login_required
def users():

    # query database to get all users's
    users = database.execute("SELECT * from users")

    # return rendered users.html page with all users
    return render_template("users.html", users = users)

# delete user route, this route can only access admin to delete some user and all user's data
@app.route("/deleteUser/<user_id>", methods = ["GET", "POST"])
@login_required
def deleteUser(user_id):

    # query database to delete user
    database.execute("DELETE FROM users WHERE id = :id", id = user_id)

    """
    if user have any books added to diary, comments, grades or posts published delete them
    query database to delete all user's books
    """
    database.execute("DELETE FROM books WHERE user_id = :user_id", user_id = user_id)

    # query database to delete all user's comments
    database.execute("DELETE FROM comments WHERE user_id = :user_id", user_id = user_id)

    # query database to delete all user's grades
    database.execute("DELETE FROM grades WHERE user_id = :user_id", user_id = user_id)

    # query database to delete all user's posts
    database.execute("DELETE FROM posts WHERE user_id = :user_id", user_id = user_id)

    # query database to get all users
    users = database.execute("SELECT * FROM users")

    # return rendered users.html page with all users
    return render_template("users.html", users = users)


# catch all other routes that doesn't exist
@app.errorhandler(404)
def page_not_found(e):

    # return rendered pageNotFound.html page
    return render_template("pageNotFound.html")
