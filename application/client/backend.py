from flask import Flask, render_template, request, redirect, url_for
#from application.server.databaseConnector import debug_print
from flask import session

import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(4)

@app.route('/')
def landing():
    sentences = (
        "Welcome to Ticket Booking. Book Tickets with one click.",
        "Fast and Easy. No Hassle.",
        "Tell us your destination and let's go!",
        "Mumbai Delhi Kolkata Chennai Bangalore Hyderabad Srinagar Sikkim.",
        "We provide the best journey possible"
    )
    return render_template('landing.html', sentences= sentences)

@app.route('/', methods=['POST'])
def handle_login():
    if 'login_type' in request.form:
        return redirect(url_for('login', login_mode= request.form['login_type']))

@app.route('/login/<login_mode>', methods=['GET', 'POST'])
def login(login_mode):
    print(login_mode)

    if('user_id' in session):
        return redirect(url_for('home'))

    if(login_mode == "signin"):
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if username != '' and password != '':
                # TODO sql check

                # session['user_id'] = username

                return redirect(url_for('home'))
            else:
                return render_template('login.html', login_mode= login_mode, error_message="Invalid credentials")
    elif(login_mode == "signup"):
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            repassword = request.form.get('repassword')

            if password == repassword:
                # TODO sql check

                # session['user_id'] = username

                return redirect(url_for('home'))
            else:
                return render_template('login.html', login_mode= login_mode, error_message="Invalid credentials")
    return render_template('login.html', login_mode= login_mode)

@app.route('/home')
def home():
    #debug_print()
    return render_template('home.html')

# For reset
def logout():
    session.clear()
    redirect(url_for('/'))

if __name__ == '__main__':
    app.run(debug=True)
