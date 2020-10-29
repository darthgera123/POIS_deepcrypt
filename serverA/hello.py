from flask import Flask, render_template, request, url_for, redirect
from werkzeug.utils import secure_filename
from forms import DataForm

app = Flask(__name__)

@app.route('/')
def hello():
    form = DataForm()
    return render_template('hello.html', form=form)

@app.route('/add', methods=['POST'])
def add():
    form = DataForm(request.form)
    if request.method == 'POST' and form.validate():
        print(request.form)
    return redirect(url_for('hello'))