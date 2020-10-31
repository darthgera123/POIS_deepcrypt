from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.utils import secure_filename
from forms import DataForm
import requests

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def hello():
    form = DataForm()
    return render_template('hello.html', form=form)

@app.route('/add', methods=['POST'])
def add():
    form = DataForm(request.form)
    if request.method == 'POST' and form.validate():
        response = requests.post("http://127.0.0.1:5000/api/model/addition", json={
            'number': request.form['number']
        })
        if response.status_code == 200:
            returned_data = response.json()
            response1 = requests.post("http://127.0.0.1:5000/api/model/subtraction", json={
                'number': returned_data
            })
            if response1.status_code == 200:
                flash(response1.json())
            else:
                flash("Issue in suctraction on server B")
        else:
            flash("Issue on Server B")
    return redirect(url_for('hello'))

if __name__=='__main__':
	# port 5000 for this and 8000 for server B
    app.run(debug=True,port=8000)
    
