# import libraries
import urllib.request
from flask import redirect, render_template, request, session
from functools import wraps

"""
Renders message as an apology to user.
Escape special characters.
https://github.com/jacebrowning/memegen#special-characters
"""
def apology(message, code = 400):
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    # return rendered apology.html page
    return render_template("apology.html", top = code, bottom = escape(message)), code

"""
Decorate route to require login.
http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
"""
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# decorate route to check if user is login. Created to don't allow user to go to login or register page through URL if it is login
def logged(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") != None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function
