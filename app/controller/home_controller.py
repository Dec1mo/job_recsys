from flask import render_template, Blueprint

home_controller = Blueprint('home_controller', __name__)

@home_controller.route('/')
def home():
    return render_template("home.html")
