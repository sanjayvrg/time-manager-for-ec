from flask import Flask
from flask import render_template 
from flask import Flask, request, session, redirect, url_for, jsonify

import os

import secrets

import firebase_admin
from firebase_admin import credentials, firestore, db

from datetime import timedelta

app = Flask(__name__, template_folder='templates')
app.secret_key = secrets.token_hex(16)

cred = credentials.Certificate('/Users/risha/TimeManager/time-manager-for-ec/json/credentials.json')
firebase_admin.initialize_app(cred, {'databaseURL': 'https://time-management-project-81b0a-default-rtdb.firebaseio.com/'})
ref = db.reference('/')

def verify_user(username, password):
    # Get a reference to the users collection in the database
    users_ref = db.collection('users')

    # Query the users collection for the provided username and password
    query = users_ref.where('username', '==', username).where('password', '==', password).get()

    # If the query returns any documents, the user is valid
    if len(query) > 0:
        return True
    else:
        return False

@app.route('/register', methods=['GET', 'POST'])
def register():
    print('hi')
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Add user data to Firebase Realtime Database
        users_ref = db.reference('users')
        new_user_ref = users_ref.push()
        new_user_ref.set({
            'id': new_user_ref.key,
            'username': username,
            'email': email,
            'password': password
        })

        session['user']['id']= new_user_ref.key

        return 'Registration successful!'
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users_ref = db.reference('users')
        query = users_ref.order_by_child('username').equal_to(username)
        result = query.get()

        if not result:
            return 'User not found'
        
        uid = list(result.keys())[0]
        user = result[uid]

        if user['password'] != password:
            return 'Incorrect password'
        
        # Log the user in (e.g. set a session variable)
        for uid, user in result.items():
            if user['password'] == password:
                # Save user information in session
                session['user'] = {
                    'id': uid,
                    'username': user['username'],
                    'email': user['email']
                }
                return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' in session:
        print(session['user'])
        user_id = session['user']['id'] # Get authenticated user's ID

        if request.method == 'POST':
            event_task = request.form['event_task']
            event_time = int(request.form['event_time'])

            # Add event data to Firebase Realtime Database for the authenticated user
            events_ref = db.reference(f'users/{user_id}/events')
            new_event_ref = events_ref.push()
            new_event_ref.set({
                'task': event_task,
                'time': event_time
            })

        # Get all events from Firebase Realtime Database for the authenticated user
        events_dict = db.reference(f'users/{user_id}/events').get()
        
        events = {}

        if events_dict is None:
            events = {}
        else:
            events = dict(events_dict)

        return render_template('dashboard.html', events=events)
    else:
        return redirect(url_for('login'))
    
@app.route('/pomodoro')
def pomodoro():
    # retrieve tasks from your real-time database
    if 'user' in session:
        print(session['user'])
        user_id = session['user']['id'] # Get authenticated user's ID

        # Get all events from Firebase Realtime Database for the authenticated user
        events_dict = db.reference(f'users/{user_id}/events').get()

        tasks = []
        total_time = 0
        current_value = 0
        if events_dict is not None:
            for task in events_dict.values():
                time_left = task['time']
                while time_left > 25:
                    tasks.append({'task': task['task'], 'time': 25 - current_value})
                    time_left -= 25 - current_value
                    total_time += 25
                    current_value = 0
        
                current_value = time_left
                tasks.append({'task': task['task'], 'time': time_left})
                total_time += time_left

            sum = 0
            numbreaks = 0
            for i in range(len(tasks)):
                #print(tasks[i]['time'])
                print(sum)
                going = False
                if sum < 25:
                    sum += tasks[i]['time']
                    going = True
                if going == True:
                    continue
                sum = 0
                tasks.insert(i + numbreaks, {'task': 'Break', 'time': 5})
                numbreaks += 1
                print(numbreaks)
                total_time += 5
            
            tasks.insert(-1, {'task': 'Break', 'time': 5})
            total_time += 5
                
                
        num_pomodoros = total_time // 25 + 1
        total_time_str = str(timedelta(minutes=total_time))

        return render_template('pomodoro.html', tasks=tasks, num_pomodoros=num_pomodoros, total_time=total_time_str)
    else:
        return redirect(url_for('login'))

@app.route('/delete/<event_id>', methods=['POST'])
def delete_event(event_id):
    user_id = session['user']['id']
    ref = db.reference(f'users/{user_id}/events')
    ref.child(event_id).delete()
    return redirect(url_for('dashboard'))


@app.route('/')
def create_app():
    return render_template('base.html')



port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
