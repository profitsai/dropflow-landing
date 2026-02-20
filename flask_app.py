from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# Note: PythonAnywhere handles the server, so we don't need any extra setup code here!
