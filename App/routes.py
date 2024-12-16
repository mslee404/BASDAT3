from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from connect import create_connection
from werkzeug.security import generate_password_hash, check_password_hash

#Create blueprint for modular routing
routes = Blueprint('routes', __name__)

#Redirect the root url to the home page
@routes.route('/')
def index():
    return redirect(url_for('routes.login'))

# Display the register
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate form inputs
        if not name or not email or not password:
            flash('Please fill in all fields.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match.', 'danger')
        else:
            # Create a database connection
            conn = create_connection()  # Assuming this function establishes a database connection
            
            if conn:
                try:
                    cursor = conn.cursor()
                    
                    # Hash the password (important for security)
                    hashed_password = generate_password_hash(password)
                    
                    # Insert the new user into the database
                    cursor.execute('''
                        INSERT INTO users (name, email, password)
                        VALUES (?, ?, ?)
                    ''', (name, email, hashed_password))
                    
                    # Commit changes and close the connection
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    flash('Registration successful! You can now log in.', 'success')
                    return redirect('/login')  # Redirect to login page
                except Exception as e:
                    # Handle cases like duplicate emails
                    flash(f'The email {email} is already registered.', 'danger')
                    conn.close()
            else:
                flash('Database connection failed.', 'danger')
    
    # Render the registration form
    return render_template('register.html')
