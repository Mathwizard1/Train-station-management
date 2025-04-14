from flask import Flask, render_template, request, redirect, url_for
from application.server.databaseConnector import DatabaseConnector
from flask import session, g

import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(4)

# Function to get database connection using Flask's g
def get_db():
    if 'db' not in g:
        try:
            dbconn = DatabaseConnector()
            dbconn.connect("TrainManagement")
            g.db = dbconn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    return g.db

# Function to close database connection
@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        try:
            # db.close()
            pass
        except Exception as e:
            print(f"Error closing database connection: {e}")

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
    dbconn = get_db()
    dbconn.set_database("TrainManagement")

    if(dbconn.errorflag):
        return render_template('login.html', login_mode= login_mode, error_message="Failed to connect Dataserver")

    if('user_id' in session):
        return redirect(url_for('home'))

    if(login_mode == "signin"):
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if (username == '' or password == ''):
                return render_template('login.html', login_mode= login_mode, error_message="Empty credentials")

            user_datas = dbconn.retrieve_values('Customers', 'Cuid, Cuname, Cupassword')

            user_found = False
            for user_data in user_datas:
                if(username == user_data[1] and password == user_data[2]):

                    user_found = True
                    session['user_id'] = user_data[0]
                    session['username'] = user_data[1]

            if user_found:
                return redirect(url_for('schedule'))
            return render_template('login.html', login_mode= login_mode, error_message="Invalid credentials")
    elif(login_mode == "signup"):
        if request.method == 'POST':
            username = request.form.get('username')
            age = request.form.get('age', None, type= int)
            gender = request.form.get('gender')
            password = request.form.get('password')
            repassword = request.form.get('repassword')

            if(username == '' or password == '' or repassword == ''
                or age is None or gender not in ['M', 'F', 'U']):
                return render_template('login.html', login_mode= login_mode, error_message="Invalid credentials")

            if password == repassword:
                dbconn = get_db()
                current_idx = dbconn.get_row_count('Customers')

                if(current_idx < 0):
                    return render_template('login.html', login_mode= login_mode, error_message="Server Error")

                dbconn.insert_entry('Customers',
                    (current_idx + 1, username, age, gender, password)            
                )

                if(dbconn.errorflag):
                    return render_template('login.html', login_mode= login_mode, error_message="Server Error")

                session['user_id'] = current_idx + 1
                session['username'] = username

                return redirect(url_for('schedule'))
            else:
                return render_template('login.html', login_mode= login_mode, error_message="Password Mismatch")
    return render_template('login.html', login_mode= login_mode)

@app.route('/schedule', methods= ['GET', 'POST'])
def schedule():
    filtering = None
    a_selected = d_selected = "All"

    if(request.method == 'POST'):
        if('defaulter' in request.form):
            filtering = None
            a_selected = d_selected = "All"
        elif('filter' in request.form):
            filtering = True
            a_selected = request.form['arv_select']
            d_selected = request.form['dep_select']

    dbconn = get_db()
    schedule, arv_stat, dep_stat = dbconn.retrieve_schedules()

    if(dbconn.errorflag):
        return render_template('schedule.html',
                               error_message= "Server Not working")

    #print(schedule)
    if(filtering):
        schedule, arv_stat, dep_stat = dbconn.retrieve_schedules()
        print(a_selected)
        print(d_selected)

    return render_template('schedule.html',
                           schedule_table= schedule,
                           arv_stat = arv_stat,
                           dep_stat = dep_stat,
                           a_selected= a_selected,
                           d_selected = d_selected)


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
