from flask import Flask, render_template, request, redirect, url_for
from application.server.databaseConnector import debug_print

app = Flask(__name__)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Dummy check
        if username == 'admin' and password == 'admin':
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/home')
def home():
    debug_print()
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
