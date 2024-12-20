from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from connect import create_connection
from werkzeug.security import generate_password_hash, check_password_hash

# Create a blueprint for modular routing
routes = Blueprint('routes', __name__)

# Redirect the root URL to the login page
@routes.route('/')
def index():
    return redirect(url_for('routes.login'))

# Display the register page
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        
        # Validate form inputs
        if not name or not email or not password:
            flash('Please fill in all fields.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match.', 'danger')
        else:
            # Create a database connection
            conn = create_connection()
            
            if conn:
                try:
                    cursor = conn.cursor()
                    
                    # Check if the email is in the allowed list
                    cursor.execute('SELECT email FROM allowed_emails WHERE email = ?', (email,))
                    allowed_email = cursor.fetchone()
                    
                    if not allowed_email:
                        flash('This email is not allowed to register.', 'danger')
                    else:
                        # Hash the password
                        hashed_password = generate_password_hash(password)
                        
                        # Insert the new user into the database
                        cursor.execute('''
                            INSERT INTO users (name, email, password, role)
                            VALUES (?, ?, ?, ?)
                        ''', (name, email, hashed_password, role))
                        
                        # Commit changes and close the connection
                        conn.commit()
                        flash('Registration successful! You can now log in.', 'success')
                        return redirect(url_for('routes.login'))  # Redirect to login page
                except Exception as e:
                    flash(f'Error: {str(e)}', 'danger')
                finally:
                    cursor.close()
                    conn.close()
            else:
                flash('Database connection failed.', 'danger')
    
    # Render the registration form
    return render_template('register.html')

# Display the login page
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validasi input form
        if not name or not email or not password:
            flash('Please fill in all fields.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match.', 'danger')
        else:
            # Buat koneksi ke database
            conn = create_connection()
            
            if conn:
                try:
                    cursor = conn.cursor()
                    
                    # Cek apakah email ada di tabel allowed_emails
                    cursor.execute('SELECT role FROM allowed_emails WHERE email = ?', (email,))
                    allowed_email = cursor.fetchone()
                    
                    if allowed_email:
                        # Dapatkan role dari tabel allowed_emails
                        role = allowed_email[0]
                        
                        # Hash password
                        hashed_password = generate_password_hash(password)
                        
                        # Simpan user baru ke tabel users
                        cursor.execute('''
                            INSERT INTO users (name, email, password, role)
                            VALUES (?, ?, ?, ?)
                        ''', (name, email, hashed_password, role))
                        
                        conn.commit()
                        flash('Registration successful! You can now log in.', 'success')
                        return redirect(url_for('routes.login'))
                    else:
                        # Jika email tidak ditemukan di allowed_emails
                        flash('This email is not allowed to register.', 'danger')
                
                except Exception as e:
                    flash(f'Error: {str(e)}', 'danger')
                finally:
                    cursor.close()
                    conn.close()
            else:
                flash('Database connection failed.', 'danger')
    
    return render_template('register.html')

# Logout the user
@routes.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('routes.login'))

# Home page placeholder (to be implemented)
@routes.route('/home')
def home():
    if 'email' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('routes.login'))
    return render_template('home.html')
