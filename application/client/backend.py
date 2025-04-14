from flask import Flask, render_template, request, redirect, url_for
from application.server.databaseConnector import DatabaseConnector
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
    session['database'] = DatabaseConnector()
    flag = session['database'].connect("TrainManagement")

    if(flag):
        return render_template('login.html', login_mode= login_mode, error_message="Failed to connect Dataserver")

    if('user_id' in session):
        return redirect(url_for('home'))

    if(login_mode == "signin"):
        if request.method == 'POST':
            session['username'] = request.form.get('username')
            password = request.form.get('password')

            user_data = session['database'].retrieve_values('Customers')

            if session['username'] != '' and password != '':
                # TODO sql check

                #session['user_id'] = userid

                return redirect(url_for('home'))
            return render_template('login.html', login_mode= login_mode, error_message="Invalid credentials")
    elif(login_mode == "signup"):
        if request.method == 'POST':
            username = request.form.get('username')
            age = request.form.get('age', None, type= int)
            gender = request.form.get('gender')
            password = request.form.get('password')
            repassword = request.form.get('repassword')

            if password == repassword:
                # TODO sql check

                # session['user_id'] = username
                session['username'] = username

                return redirect(url_for('home'))
            else:
                return render_template('login.html', login_mode= login_mode, error_message="Invalid credentials")
    return render_template('login.html', login_mode= login_mode)

@app.route('/home', methods= ['GET', 'POST'])
def home():
    if('username' in session):
        form_fields = [
        {'name': 'name', 'label': 'Name', 'type': 'text'},
        {'name': 'email', 'label': 'Email', 'type': 'email'},
        {'name': 'age', 'label': 'Age', 'type': 'number'},
        ]
        train_headers = ["Select", 'Train', 'Arv. Station', 'Arv. Time', 'Dep. Station', 'Dep. Time']
        train_data = [
            (3, 'Train', 'Arv. Station', 'Arv. Time', 'Dep. Station', 'Dep. Time'),
            (4, 'Train', 'Arv. Station', 'Arv. Time', 'Dep. Station', 'Dep. Time'),
            (5, 'Train', 'Arv. Station', 'Arv. Time', 'Dep. Station', 'Dep. Time')
        ]
        data_len = len(train_headers)

        # if request.method == 'POST':
        #     form_data = request.form.to_dict()
        #     print("Form Data:", form_data)
        #     #  Here you would process the form data (e.g., save to a database)
        #     table_data.append(form_data) # just add to table_data for display
        #     return render_template('home.html', 
        #             form_fields=form_fields, 
        #             table_headers=table_headers, 
        #             table_data=table_data)

        return render_template('home.html', 
                table_headers= train_headers, 
                table_data= train_data,
                row_len= data_len,
                selected_row = 1)
    return logout()

# For reset session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login', login_mode= 'signin'))

if __name__ == '__main__':
    app.run(debug=True)
