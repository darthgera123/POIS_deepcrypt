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

if __name__=='__main__':
	# port 5000 for this and 8000 for server B
    app.run(debug=True,port=8000)
    
