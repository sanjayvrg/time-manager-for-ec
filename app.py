from flask import Flask
from flask import render_template 

import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

cred = credentials.Certificate('/path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get the form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Add the user data to the Firestore DB
        doc_ref = db.collection('users').document(email)
        doc_ref.set({
            'name': name,
            'email': email,
            'password': password
        })

        # Redirect the user to the home page
        return redirect('/')

    # Render the registration page template
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Verify the user's credentials
        if verify_user(username, password):
            # Set the 'user' key in the session object
            session['user'] = username

            # Redirect the user to the home page
            return redirect('/')

    # Render the login page template
    return render_template('login.html')

@app.route('/')
def create_app():
    return render_template('base.html')

if __name__ == '__main__':
    app.run(debug=True)

