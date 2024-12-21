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
                    cursor.execute('SELECT users.email, users.password, email_role.role FROM users JOIN email_role ON email_role.email = users.email WHERE email_role.email = ?', (email))
                    user = cursor.fetchone()
                    
                    if user:
                        # Cek password
                        email, stored_password, role = user
                        if check_password_hash(stored_password, password):
                            # Login berhasil, simpan email ke session
                            session['email'] = email
                            session['role'] = role
                            flash('Login successful!', 'success')
                            return redirect(url_for('routes.home',role=role))
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
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('routes.login'))

# Home page placeholder (to be implemented)
@routes.route('/home')
def home():
    if 'email' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('routes.login'))
    
    role = session.get('role')
    return render_template('home.html', role=role)

@routes.route('/home/search_show/<show_id>', methods=['GET', 'POST'])
def search_show():
    if request.method == 'POST':
        queryShow = request.form['queryShow']

        conn = create_connection()

        if conn:
            try:
                return render_template('/viewshow.html', queryShow=queryShow)
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
                return render_template('home.html')

@routes.route('/viewshow.html', methods=['GET'])
def viewshow():
    if 'email' in session:
        conn = create_connection()

        queryShow = request.args.get('queryShow') if request.method == 'GET' else request.form.get('queryShow')
        role = session.get('role')

        if not queryShow:
            flash('No result found', 'warning')
            return redirect(url_for('routes.home'))

        if conn:
            try:
                cursor = conn.cursor()

                # Dua-duanya bisa liat
                cursor.execute('SELECT * FROM fix_show WHERE tconst = ?', queryShow)
                basic = cursor.fetchall()

                cursor.execute('SELECT * FROM fix_titleakas WHERE tconst = ?', queryShow)
                akas = cursor.fetchall()

                cursor.execute('SELECT * FROM fix_titleepisode WHERE tconst = ?', queryShow)
                episode = cursor.fetchall()

                cursor. execute('SELECT pc.tconst, pct.companyName FROM fix_productioncompany pc JOIN fix_productioncompanytype pct ON pc.companyNameID = pct.companyNameID WHERE pc.tconst = ?', queryShow)
                productioncompany = cursor.fetchall()

                cursor.execute('SELECT * FROM fix_rating WHERE tconst = ?', queryShow)
                rating = cursor.fetchall()

                cursor.execute('SELECT pc.tconst, pct.prodCountryName, oct.originCountryName fix_productioncountry pc JOIN fix_productioncountrytype pct ON pc.prodCountryID = pct.prodCountryID JOIN fix_origincountrytype oct ON oct.originCountryID = pc.originCountryID WHERE tconst = ?', queryShow)
                productioncountry = cursor.fetchall()

                cursor.execute('SELECT sg.tconst, g.genreName FROM fix_showgenre sg JOIN fix_genre g ON sg.genreID = g.genreID WHERE sg.tconst = ?', queryShow)
                genres = cursor.fetchall()

                cursor.execute('SELECT sd.tconst, nb.primaryName FROM fix_showdirector sd JOIN fix_namebasic nb ON nb.nconst = sd.nconst WHERE sd.tconst = ?', queryShow)
                directors = cursor.fetchall()

                cursor.execute('SELECT sw.tconst, nb.primaryName FROM fix_showwriter sw JOIN fix_namebasic nb ON nb.nconst = sw.nconst WHERE sw.tcosnt = ?', queryShow)
                writers = cursor.fetchall()

                # eksekutif doang yang bisa lihat
                if role == 'eksekutif':
                    cursor.execute('SELECT isFirst, date FROM fix_airdate WHERE tconst = ?', queryShow)
                    airdates = cursor.fetchall()

                    cursor.execute('SELECT lt.linkTypeName, l.link FROM fix_link l JOIN fix_linktype lt ON l.linkTypeID = lt.linkTypeID WHERE l.tconst = ?', queryShow)
                    links = cursor.fetchall()

                    # produser doang yang bisa liat
                if role == 'produser':
                    cursor.execute('SELECT lt.languageType, l.tconst FROM fix_language l JOIN fix_languagetype lt ON l.languageID = lt.languageID WHERE l.tconst = ?', queryShow)
                    language = cursor.fetchall()

                    cursor.execute('SELECT sl.tconst, slt.spoken_language_name FROM fix_spokenlanguage sl JOIN fix_spokenlanguagetype slt ON slt.spoken_language_type_id = sl.spokenLanguageID WHERE sl.tcsont = ?', queryShow)
                    spokenlanguage = cursor.fetchall()

                return render_template(
                    'viewshow.html',
                    queryShow=queryShow,
                    role=role,
                    basic=basic,
                    akas=akas,
                    episode=episode,
                    productioncompany=productioncompany,
                    productioncountry=productioncountry,
                    rating=rating,
                    genres=genres,
                    directors=directors,
                    writers=writers,
                    airdates=airdates,
                    links=links,
                    language=language,
                    spokenlanguage=spokenlanguage,
                )
            except Exception as e:
                flash(f'error: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()

        return redirect(url_for('routes.home'))

