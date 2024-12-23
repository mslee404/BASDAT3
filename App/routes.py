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

        if not name or not email or not password:
            flash('Please fill in all fields.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match.', 'danger')
        else:
            conn = create_connection()

            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        flash('Email is already registered.', 'danger')
                    else:
                        cursor.execute('SELECT role FROM email_role WHERE email = ?', (email,))
                        allowed_email = cursor.fetchone()

                        if allowed_email:
                            role = allowed_email[0]
                            hashed_password = generate_password_hash(password)
                            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
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

        if not email or not password:
            flash('Please fill in all fields.', 'danger')
        else:
            conn = create_connection()

            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(''' 
                        SELECT users.email, users.password, email_role.role 
                        FROM users 
                        JOIN email_role ON email_role.email = users.email 
                        WHERE email_role.email = ? 
                    ''', (email,))
                    user = cursor.fetchone()

                    if user:
                        email, stored_password, role = user
                        if check_password_hash(stored_password, password):
                            session['email'] = email
                            session['role'] = role
                            flash('Login successful!', 'success')
                            return redirect(url_for('routes.home', role=role))
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

@routes.route('/home/search_show', methods=['GET', 'POST'])
def search_show():
    if request.method == 'POST':
        queryShow = request.form['queryShow']
        conn = create_connection()

        if conn:
            try:
                return redirect(url_for('routes.viewshow', queryShow=queryShow))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
                return render_template('home.html')

@routes.route('/home/search_person', methods=['GET', 'POST'])
def search_person():
    if request.method == 'POST':
        queryPerson = request.form['queryPerson']
        conn = create_connection()

        if conn:
            try:
                return redirect(url_for('routes.viewperson', queryPerson=queryPerson))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
                return render_template('home.html')


@routes.route('/viewshow/<queryShow>', methods=['GET'])
def viewshow(queryShow):
    if 'email' in session:
        conn = create_connection()
        role = session.get('role')

        if not queryShow:
            flash('No result found', 'warning')
            return redirect(url_for('routes.home'))

        if conn:
            try:
                cursor = conn.cursor()

                # Debugging: Cek nilai queryShow yang diterima
                print(f"Query Show: {queryShow}")

                cursor.execute('SELECT * FROM fix_show WHERE tconst = ?', (queryShow,))
                basic = cursor.fetchall()

                # Perbaiki pengambilan nama kolom dengan cursor.description
                basic_columns = [desc[0] for desc in cursor.description]
                basic_dict = [dict(zip(basic_columns, row)) for row in basic]

                # Debugging: Cek hasil query
                if not basic_dict:
                    flash(f'No results found for {queryShow}', 'warning')

                # Lakukan hal yang sama untuk tabel-tabel lainnya...
                cursor.execute('SELECT * FROM fix_titleakas WHERE tconst = ?', (queryShow,))
                akas = cursor.fetchall()
                akas_columns = [desc[0] for desc in cursor.description]
                akas_dict = [dict(zip(akas_columns, row)) for row in akas]

                cursor.execute('SELECT * FROM fix_titleepisode WHERE tconst = ?', (queryShow,))
                episode = cursor.fetchall()
                episode_columns = [desc[0] for desc in cursor.description]
                episode_dict = [dict(zip(episode_columns, row)) for row in episode]

                cursor.execute(''' 
                    SELECT pc.tconst, pct.companyName
                    FROM fix_productioncompany pc 
                    JOIN fix_productioncompanytype pct 
                    ON pc.companyNameID = pct.companyNameID
                    WHERE pc.tconst = ? 
                ''', (queryShow,))
                productioncompany = cursor.fetchall()

                cursor.execute('SELECT tp.ordering, nb.primaryName, tp.category, tp.job, tp.characters FROM fix_titleprincipal tp JOIN fix_namebasic nb ON tp.nconst = nb.nconst WHERE tp.tconst = ?', (queryShow,))
                principals = cursor.fetchall()
                episode_columns = [desc[0] for desc in cursor.description]
                episode_dict = [dict(zip(episode_columns, row)) for row in episode]

                cursor.execute(''' 
                    SELECT tp.ordering, nb.primaryName, tp.category, tp.job, tp.characters
                    FROM fix_titleprincipal tp 
                    JOIN fix_namebasic nb 
                    ON tp.nconst = nb.nconst
                    WHERE tp.tconst = ? 
                ''', (queryShow,))
                principals = cursor.fetchall()

                cursor.execute('SELECT * FROM fix_rating WHERE tconst = ?', (queryShow,))
                rating = cursor.fetchall()

                # production country
                cursor.execute(''' 
                    SELECT pc.tconst, pct.prodCountryName, oct.originCountryName 
                    FROM fix_productioncountry pc 
                    JOIN fix_productioncountrytype pct 
                    ON pc.prodCountryID = pct.prodCountryID 
                    JOIN fix_origincountrytype oct 
                    ON oct.originCountryID = pc.originCountryID 
                    WHERE pc.tconst = ? 
                ''', (queryShow,))
                productioncountry = cursor.fetchall()

                cursor.execute(''' 
                    SELECT distinct sg.tconst, g.genreName 
                    FROM fix_showgenre sg 
                    JOIN fix_genre g 
                    ON sg.genreID = g.genreID 
                    WHERE sg.tconst = ? 
                ''', (queryShow,))
                genres = cursor.fetchall()

                cursor.execute(''' 
                    SELECT sd.tconst, nb.primaryName 
                    FROM fix_showdirector sd 
                    JOIN fix_namebasic nb 
                    ON nb.nconst = sd.nconst 
                    WHERE sd.tconst = ? 
                ''', (queryShow,))
                directors = cursor.fetchall()

                cursor.execute(''' 
                    SELECT sw.tconst, nb.primaryName 
                    FROM fix_showwriter sw 
                    JOIN fix_namebasic nb 
                    ON nb.nconst = sw.nconst 
                    WHERE sw.tconst = ? 
                ''', (queryShow,))
                writers = cursor.fetchall()

                airdates, links, language, spokenlanguage, networks = [], [], [], [], []

                if role == 'eksekutif':
                    cursor.execute('SELECT isFirst, date FROM fix_airdate WHERE tconst = ?', (queryShow,))
                    airdates = cursor.fetchall()

                    cursor.execute(''' 
                        SELECT lt.linkTypeName, l.link 
                        FROM fix_link l 
                        JOIN fix_linktype lt 
                        ON l.linkTypeID = lt.linkTypeID
                        WHERE l.tconst = ? 
                    ''', (queryShow,))
                    links = cursor.fetchall()

                    cursor.execute('SELECT nt.networkName FROM fix_network n JOIN fix_networktype nt ON n.networkTypeID = nt.networkTypeID WHERE n.tconst = ?', (queryShow,))
                    networks = cursor.fetchall()

                if role == 'produser':
                    cursor.execute(''' 
                        SELECT lt.languageType, l.tconst 
                        FROM fix_language l 
                        JOIN fix_languagetype lt 
                        ON l.languageID = lt.languageID 
                        WHERE l.tconst = ? 
                    ''', (queryShow,))
                    language = cursor.fetchall()

                    cursor.execute(''' 
                        SELECT sl.tconst, slt.spoken_language_name 
                        FROM fix_spokenlanguage sl 
                        JOIN fix_spokenlanguagetype slt 
                        ON slt.spoken_language_type_id = sl.spokenLanguageID 
                        WHERE sl.tconst = ? 
                    ''', (queryShow,))
                    spokenlanguage = cursor.fetchall()

                return render_template(
                    'viewshow.html',
                    queryShow=queryShow,
                    role=role,
                    basic=basic_dict,
                    akas=akas_dict,
                    episode=episode_dict,
                    productioncompany=productioncompany,
                    productioncountry=productioncountry,
                    rating=rating,
                    networks=networks,
                    principals=principals,
                    genres=genres,
                    directors=directors,
                    writers=writers,
                    airdates=airdates,
                    links=links,
                    language=language,
                    spokenlanguage=spokenlanguage,
                )
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()

        return redirect(url_for('routes.home'))

@routes.route('/viewperson/<queryPerson>', methods=['GET'])
def viewperson(queryPerson):
    if 'email' in session:
        conn = create_connection()
        role = session.get('role')

        if not queryPerson:
            flash('No result found', 'warning')
            return redirect(url_for('routes.home'))

        if conn:
            try:
                cursor = conn.cursor()

                # Debugging: Cek nilai queryPerson yang diterima
                print(f"Query Person: {queryPerson}")

                cursor.execute('SELECT * FROM fix_namebasic WHERE nconst = ?', (queryPerson,))
                namebasic = cursor.fetchall()

                # Debugging: Cek hasil query
                if not namebasic:
                    flash(f'No results found for {queryPerson}', 'warning')

                # Lakukan hal yang sama untuk tabel-tabel lainnya...
                cursor.execute('SELECT * FROM fix_primaryprofession WHERE nconst = ?', (queryPerson,))
                primaryprofession = cursor.fetchall()
                primaryprofession_columns = [desc[0] for desc in cursor.description]
                primaryprofession_dict = [dict(zip(primaryprofession_columns, row)) for row in primaryprofession]

                cursor.execute('SELECT s.primaryTitle FROM fix_knownfortitle kft JOIN fix_show s ON kft.tconst = s.tconst WHERE nconst = ?', (queryPerson,))
                knownfortitle = cursor.fetchall()
                knownfortitle_columns = [desc[0] for desc in cursor.description]
                knownfortitle_dict = [dict(zip(knownfortitle_columns, row)) for row in knownfortitle]

                return render_template(
                    'viewperson.html',
                    queryPerson=queryPerson,
                    role=role,
                    namebasic=namebasic,
                    primaryprofession=primaryprofession,
                    knownfortitle=knownfortitle,
                )
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()

        return redirect(url_for('routes.home'))

@routes.route('/deleteprincipal/<tconst><ordering>', methods=['POST'])
def delete_principal(tconst, ordering):
    if 'email' in session:
        queryShow = request.args.get('queryShow')
        conn = create_connection()
        
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM fix_titleprincipal WHERE tconst = ? AND ordering = ?', (tconst, ordering,))
                conn.commit()  # Commit the transaction
                
                # Redirect to the continent list with a success message
                flash('Principal deleted successfully!', 'success')
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()  # Ensure the connection is closed
        else:
            flash('Error: Unable to connect to the database.', 'danger')
        
        return redirect(url_for('routes.viewshow', queryShow=queryShow))
    else:
        return redirect(url_for('routes.login'))