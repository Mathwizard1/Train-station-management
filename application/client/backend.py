from flask import Flask, render_template, request, redirect, url_for
from application.server.databaseConnector import DatabaseConnector
from schedulecycle import scheduler_call

from flask import session, g
from flask import jsonify

import multiprocessing
import threading
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
            db.close()
        except Exception as e:
            print(f"Error closing database connection: {e}")

@app.route('/')
def landing():
    sentences = (
        "Welcome to Train Booking. Book Tickets with one click.",
        "By Anshurup, Tejeshwar, Siddarth"
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
        return redirect(url_for('schedule'))

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
                    session.permanent = True

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

    if('user_id' in session):
        if(request.method == 'POST'):
            if('defaulter' in request.form):
                filtering = None
                a_selected = d_selected = "All"
            elif('filter' in request.form):
                filtering = True
                a_selected = request.form['arv_select']
                d_selected = request.form['dep_select']
            elif('submit' in request.form):
                if('selected_row' in request.form):
                    #print(request.form['selected_row'])
                    session['schedule_id'] = request.form['selected_row']
                    session['ticket_booked'] = "booking"
                    return redirect((url_for('ticket')))

        dbconn = get_db()
        schedule, arv_stat, dep_stat = dbconn.retrieve_schedules()

        if(dbconn.errorflag):
            return render_template('schedule.html',
                                   error_message= "Server Not working")

        if(filtering):
            schedule, arv_stat, dep_stat = dbconn.retrieve_schedules(d_selected, a_selected)
            #print(a_selected)
            #print(d_selected)
        #print(schedule)

        return render_template('schedule.html',
                               schedule_table= schedule,
                               arv_stat = arv_stat,
                               dep_stat = dep_stat,
                               a_selected= a_selected,
                               d_selected = d_selected)
    return redirect(url_for('logout'))

@app.route('/ticket', methods= ['GET', 'POST'])
def ticket():
    dbconn = get_db()

    sentences = (
        "Welcome to Train Booking. Book Tickets with one click.",
        "By Anshurup, Tejeshwar, Siddarth"
        "Fast and Easy. No Hassle.",
        "Tell us your destination and let's go!",
        "Mumbai Delhi Kolkata Chennai Bangalore Hyderabad Srinagar Sikkim.",
        "We provide the best journey possible"
    )

    if('user_id' in session and 'schedule_id' in session):
        if(request.method == "POST"):
            if(session['ticket_booked'] != 'booked'):
                if('back' in request.form):
                    session.pop('schedule_id', None)
                    session.pop('train', None)
                    session.pop('coach', None)

                    return redirect(url_for('schedule'))
                elif('submit' in request.form and 
                    'coach_selections' in request.form and request.form['coach_selections'] != ""):
                    coach = request.form['coach_selections']
                    session['coach'] = coach

                    rac_status = False
                    if('racval' in request.form):
                        rac_status = True

                    seat_num, rac_type = dbconn.create_ticket(
                                            train= session['train'], coach= session['coach'],
                                            custid= session['user_id'],
                                            give_rac= rac_status, check_available= True)
                    
                    if(seat_num != -1):
                        session['seat'] = seat_num
                        session['rac'] = "Yes" if(rac_type) else "No"
                        session['ticket_booked'] = 'booked'
                        return redirect(url_for('ticket'))

                    if('waitval' in request.form):
                        session['ticket_booked'] = 'waiting'
                        dbconn.create_waiting(session['train'], session['coach'], session['user_id'])
                        return redirect(url_for('waiting'))

                    session['ticket_booked'] = 'no_ticket'
                    return redirect(url_for('ticket'))
            elif('cancel' in request.form):
                dbconn.cancel_ticket(session['user_id'], session['train'], session['coach'])
                session.pop('schedule_id', None)
                session.pop('train', None)
                session.pop('coach', None)

                session['ticket_booked'] = 'cancelled'
                return render_template('ticket.html', sentences=sentences, ticket_booked= session['ticket_booked'])

        if(session['ticket_booked'] == 'cancelled' or session['ticket_booked'] == 'no_ticket'):
            return render_template('ticket.html', sentences=sentences, ticket_booked= session['ticket_booked'])       
        
        train_data, _, _ = dbconn.retrieve_schedules(where=f"WHERE Shid={session['schedule_id']}")
        if(dbconn.errorflag):
            return render_template('ticket.html', sentences=sentences, error_message="SERVER ERROR")

        train_data = train_data[0]
        session['train'] = train_data[1]

        # use train id and get coaches list
        customer_data = dbconn.get_customer_data(session['user_id'])
        coachs = dbconn.train_coach_retriver(train_data[1])

        if(dbconn.errorflag):
            return render_template('ticket.html', sentences=sentences, error_message="SERVER ERROR")

        print(customer_data)
        print(train_data)

        param_dict = {
            'name': customer_data['Cuname'],
            'age': customer_data['Cuage'],
            'gender': customer_data['Cugender'],

            'coachs': coachs,

            'train_name': train_data[1],
            'arv_station': train_data[2],
            'arv_time': train_data[3],
            'dep_station': train_data[4],
            'dep_time': train_data[5],

            'ticket_booked': session['ticket_booked']
        }

        if(session['ticket_booked'] == 'booked'):
            param_dict.pop('coachs', None)
            param_dict['coach'] = session['coach']

            param_dict['ticket_id'] = session
            param_dict['seat'] = session['seat']
            param_dict['rac'] = session['rac']

        return render_template('ticket.html', sentences=sentences, 
                    **param_dict)
    
    elif('user_id' in session):
        return redirect(url_for('schedule'))
    return redirect(url_for('logout'))

@app.route('/check_Waiting_List')
def check_Waiting_List():
    if('user_id' in session and 'train' in session and 'coach' in session):
        dbconn = get_db()
        current_status = dbconn.check_waiting(session['user_id'], session['train'], session['coach'])
        train_id = dbconn.train_id_retriever(session['train'])

        ticket_val = dbconn.retrieve_values('tickets', 'Tiseatnum,TiRACstatus', f"WHERE TiTrid={train_id} and TiConame= '{session['coach']}' and TiCuid={session['user_id']}")
        if(dbconn.errorflag):
            return jsonify({"status": "waiting"})

        session['seat'] = ticket_val[0][0]
        session['rac'] = ticket_val[0][1]

        if current_status:
            return jsonify({"status": "waiting"})
        else:
            session['ticket_booked'] = 'booked'
            return jsonify({"status": "changed", "redirect_url": url_for('ticket')})
    return jsonify({"status": "changed", "redirect_url": url_for('logout')})

@app.route('/waiting', methods= ['GET', 'POST'])
def waiting():
    dbconn = get_db()

    if('schedule_id' in session and 'coach' in session and 'user_id' in session):
        if(request.method == "POST" and 'cancel' in request.form):
            # dbconn.cancel_ticket(session['user_id'], session['train'], session['coach'])
            session.pop('train', None)
            session.pop('coach', None)

            session['ticket_booked'] = 'cancelled'
            return redirect(url_for('ticket'))

        train_data, _, _ = dbconn.retrieve_schedules(where=f"WHERE Shid={session['schedule_id']}")
        if(dbconn.errorflag):
            return render_template('ticket.html', error_message="SERVER ERROR")

        train_data = train_data[0]
        customer_data = dbconn.get_customer_data(session['user_id'])

        if(dbconn.errorflag):
            return render_template('ticket.html', error_message="SERVER ERROR")

        param_dict = {
            'name': customer_data['Cuname'],
            'age': customer_data['Cuage'],
            'gender': customer_data['Cugender'],

            'coach': session['coach'],

            'train_name': train_data[1],
            'arv_station': train_data[2],
            'arv_time': train_data[3],
            'dep_station': train_data[4],
            'dep_time': train_data[5],

            'ticket_booked': session['ticket_booked']
        }

        return render_template('ticket.html', **param_dict)
    return redirect(url_for('ticket'))

# For reset session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login', login_mode="signin"))

if __name__ == '__main__':
    ports = [5000, 5001]
    threads = []

    proc = multiprocessing.Process(
        target= scheduler_call
    )
    proc.start()

    app.run(debug=True, port= ports[0])
    exit()

    # for port in ports:
    #     t = threading.Thread(target= app.run, kwargs={'debug':False,'port': port})
    #     t.start()
    #     threads.append(t)

    # for thread in threads:
    #     thread.join()