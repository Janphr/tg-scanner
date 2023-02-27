from flask import render_template
from flask_classful import FlaskView


class IndexView(FlaskView):

    def index(self):
        print("index.html Requested")
        return render_template('index.html')