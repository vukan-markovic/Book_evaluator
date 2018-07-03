# import libraries
import urllib.request
from flask import redirect, render_template, request, session
from functools import wraps

# renders message as an apology to user
def apology(message, code = 400):
    def escape(s):

        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    # return rendered apology.html page
    return render_template("apology.html", top = code, bottom = escape(message)), code

# function to require login
def login_required(f):

    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function