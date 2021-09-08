import os 
import sys

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, '..'))

from flask import Flask

from app.parameters import APP_HOST, APP_PORT
from app.controller.home_controller import home_controller
from app.controller.result_controller import result_controller
from app.controller.skill_controller import skill_controller

app = Flask(__name__)

app.register_blueprint(home_controller)
app.register_blueprint(result_controller)
app.register_blueprint(skill_controller)

if __name__ == '__main__':
    app.run(host=APP_HOST, port=APP_PORT, debug=True)

