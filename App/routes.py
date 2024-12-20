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

                    # Cek apakah email sudah terdaftar di tabel users
                    cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
                    existing_user = cursor.fetchone()
                    
                    if existing_user:
                        flash('Email is already registered.', 'danger')
                    else:
                        # Cek apakah email ada di tabel email_role
                        cursor.execute('SELECT role FROM email_role WHERE email = ?', (email,))
                        allowed_email = cursor.fetchone()
                        
                        if allowed_email:
                            # Dapatkan role dari tabel email_role
                            role = allowed_email[0]
                            
                            # Hash password
                            hashed_password = generate_password_hash(password)
                            
                            # Simpan user baru ke tabel users
                            cursor.execute(''' 
                                INSERT INTO users (name, email, password)
                                VALUES (?, ?, ?)
                            ''', (name, email, hashed_password))
                            
                            conn.commit()
                            flash('Registration successful! You can now log in.', 'success')
                            return redirect(url_for('routes.login'))
                        else:
                            flash('This email is not allowed to register.', 'danger')
                
                except Exception as e:
                    flash(f'Error: {str(e)}', 'danger')
                finally:
                    cursor.close()
                    conn.close()
            else:
                flash('Database connection failed.', 'danger')
    
    return render_template('register.html')

# Display the login page
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Validasi input form
        if not email or not password:
            flash('Please fill in all fields.', 'danger')
        else:
            # Buat koneksi ke database
            conn = create_connection()
            
            if conn:
                try:
                    cursor = conn.cursor()
                    
                    # Cek apakah email ada di tabel users
                    cursor.execute('SELECT email, password FROM users WHERE email = ?', (email,))
                    user = cursor.fetchone()
                    
                    if user:
                        # Cek password
                        stored_password = user[1]
                        if check_password_hash(stored_password, password):
                            # Login berhasil, simpan email ke session
                            session['email'] = email
                            flash('Login successful!', 'success')
                            return redirect(url_for('routes.home'))
                        else:
                            flash('Invalid password.', 'danger')
                    else:
                        flash('Email not registered.', 'danger')
                
                except Exception as e:
                    flash(f'Error: {str(e)}', 'danger')
                finally:
                    cursor.close()
                    conn.close()
            else:
                flash('Database connection failed.', 'danger')
    
    return render_template('login.html')

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