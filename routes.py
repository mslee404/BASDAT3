from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from connect import create_connection
from werkzeug.security import generate_password_hash, check_password_hash

# Create a blueprint for modular routing
routes = Blueprint('routes', __name__)

# Redirect the root URL to the home page
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
        role = request.form['role']
        
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
                        INSERT INTO users (name, email, password, role)
                        VALUES (?, ?, ?, ?)
                    ''', (name, email, hashed_password, role))
                    
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

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Create a connection to the database
        conn = create_connection()
        
        if conn:
            cursor = conn.cursor()
            
            # Query only the hashed password for the provided email
            cursor.execute('SELECT password, role FROM Users WHERE email = ?', (email))
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if user:
                hashed_password = user[0]
                role = user[1]
                
                # Verify the hashed password
                if check_password_hash(hashed_password, password):
                    # Fill the session with the user's email
                    session['email'] = email
                    session['role'] = role
                    flash('Login successful!', 'success')
                    return redirect(url_for('routes.home'))
                else:
                    flash('Invalid email or password', 'danger')
            else:
                flash('Invalid email or password', 'danger')
        else:
            flash('Failed to connect to the database', 'danger')
        
    return render_template('login.html')

# Logout the user
@routes.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('routes.login'))

# Display the home page
@routes.route('/home')
def home():
    if 'email' in session:
        return render_template('home.html', role=session['role'])
    else:
        return redirect(url_for('routes.login'))

# Display the list of top 10 countries 
# @routes.route('/country')
# def country():
#     if 'email' in session:
#         # Get a connection to the database
#         conn = create_connection()
        
#         # Check if the connection was successful
#         if conn:
#             # Create a cursor from the connection
#             cursor = conn.cursor()
            
#             # Execute a query
#             cursor.execute('SELECT TOP 10 Code, Name, Capital, FORMAT(Population, \'N0\') AS Population, FORMAT(Area, \'N0\') AS Area FROM Country')
            
#             # Fetch the results
#             countries = cursor.fetchall()
            
#             # Close the cursor and connection
#             cursor.close()
#             conn.close()
            
#             # Pass the results to the template
#             return render_template('country.html', countries=countries)
#         else:
#             return render_template('country.html', countries=None)
#     else:
#         return redirect(url_for('routes.login'))

# Display the list of countries with pagination
@routes.route('/country')
def country():
    if 'email' in session:
        
        if session['role'] == 'continent':
            return redirect(url_for('routes.home'))
        
        # Get the current page number from the query string (default to page 1)
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of items per page
        
        # Calculate the starting row for the query (offset)
        offset = (page - 1) * per_page
        
        # Get a connection to the database
        conn = create_connection()
        
        if conn:
            # Create a cursor from the connection
            cursor = conn.cursor()
            
            # Execute a query with pagination using OFFSET and FETCH NEXT
            cursor.execute('''
                SELECT Code, Name, Capital, FORMAT(Population, 'N0') AS Population, FORMAT(Area, 'N0') AS Area
                FROM Country
                ORDER BY Name  -- or any other column for sorting
                OFFSET ? ROWS
                FETCH NEXT ? ROWS ONLY
            ''', (offset, per_page))
            
            # Fetch the results
            countries = cursor.fetchall()
            
            # Get the total count of rows to calculate the number of pages
            cursor.execute('SELECT COUNT(*) FROM Country')
            total_count = cursor.fetchone()[0]
            
            # Close the cursor and connection
            cursor.close()
            conn.close()
            
            # Calculate total number of pages
            total_pages = (total_count + per_page - 1) // per_page
            
            # Pass the results, total pages, and current page to the template
            return render_template('country.html', countries=countries, total_pages=total_pages, current_page=page)
        else:
            return render_template('country.html', countries=None)
    else:
        return redirect(url_for('routes.login'))
# Display the list of continents
@routes.route('/continent')
def continents():
    if 'email' in session:
        
        if session['role'] == 'country':
            return redirect(url_for('routes.home'))
        
        # Get a connection to the database
        conn = create_connection()
        
        # Check if the connection was successful
        if conn:
            # Create a cursor from the connection
            cursor = conn.cursor()
            
            # Execute a query
            cursor.execute('''
                SELECT Name AS Name, FORMAT(Area, 'N1') AS Area FROM continent
            ''')
            
            # Fetch the results
            continents = cursor.fetchall()
            
            # Close the cursor and connection
            cursor.close()
            conn.close()
            
            # Pass the results to the template
            return render_template('continent.html', continents=continents)
        else:
            return render_template('continent.html', continents=None)
    else:
        return redirect(url_for('routes.login'))
    
# Display the form to create a new continent
@routes.route('/continent/create', methods=['GET', 'POST'])
def create_continent():
    if 'email' in session:
        
        # if country role want to access continent page
        # it will redirect to country page
        if session['role'] == 'country':
            return redirect(url_for('routes.home'))
        
        # Handle the form submission when the method is POST
        if request.method == 'POST':
            continent_name = request.form['name']
            continent_area = request.form['area']
            
            # Get a connection to the database
            conn = create_connection()
            
            # Check if the connection was successful
            if conn:
                cursor = conn.cursor()
                try:
                    # Insert the new continent into the database
                    cursor.execute('INSERT INTO continent (Name, Area) VALUES (?, ?)', (continent_name, continent_area))
                    conn.commit()  # Commit the transaction
                    
                    # Redirect to the continent list with a success message
                    flash('Continent added successfully!', 'success')
                    return redirect(url_for('routes.continents'))
                except Exception as e:
                    flash(f'Error: {str(e)}', 'danger')  # Flash error message
                finally:
                    cursor.close()
                    conn.close()
            
            flash('Failed to connect to the database', 'danger')  # Error if connection failed

        # Render the form for GET request
        return render_template('create_continent.html')
    else:
        return redirect(url_for('routes.login'))

# Delete a continent
@routes.route('/continent/delete/<name>', methods=['POST'])
def delete_continent(name):
    if 'email' in session:
        if session['role'] == 'country':
            return redirect(url_for('routes.home'))
        
        # Get a connection to the database
        conn = create_connection()
        
        # Check if the connection was successful
        if conn:
            cursor = conn.cursor()
            try:
                # Delete the continent from the database
                cursor.execute('DELETE FROM continent WHERE Name = ?', (name,))
                conn.commit()  # Commit the transaction
                
                # Redirect to the continent list with a success message
                flash('Continent deleted successfully!', 'success')
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()  # Ensure the connection is closed
        else:
            flash('Error: Unable to connect to the database.', 'danger')
        
        return redirect(url_for('routes.continents'))
    else:
        return redirect(url_for('routes.login'))

# Update a continent
@routes.route('/continent/update/<name>', methods=['GET', 'POST'])
def update_continent(name):
    if 'email' in session:
        
        if session['role'] == 'country':
            return redirect(url_for('routes.home'))
        
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Decode the name if it's URL-encoded
                name = name.replace('%20', ' ')  # Handle spaces, if needed

                if request.method == 'POST':
                    # Get updated data from the form
                    new_name = request.form['name']
                    area = request.form['area']

                    # Update the continent in the database
                    cursor.execute('UPDATE continent SET Name = ?, Area = ? WHERE Name = ?', (new_name, area, name))
                    conn.commit()

                    flash('Continent updated successfully!', 'success')
                    return redirect(url_for('routes.continents'))

                # For GET request, fetch current data to pre-fill the form
                cursor.execute('SELECT Name, Area FROM continent WHERE Name = ?', (name,))
                continent = cursor.fetchone()
                if not continent:
                    flash('Continent not found!', 'danger')
                    return redirect(url_for('routes.continents'))

                # Pass the current data to the form
                return render_template('update_continent.html', continent={'name': continent[0], 'area': continent[1]})
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()
        else:
            flash('Error: Unable to connect to the database.', 'danger')
            return redirect(url_for('routes.continents'))
    else:
        return redirect(url_for('routes.login'))
    
# Get list of resources in the country
@routes.route('/country/resources', methods=['GET'])
def country_resources_search():
    if 'email' in session:
        if session['role'] == 'continent':
            return redirect(url_for('routes.home'))
        
        country_code = request.args.get('country_code')
        conn = create_connection()

        try:
            cursor = conn.cursor()

            # Execute the stored procedure with the country code
            cursor.execute("EXEC sp_country_resources @Country=?", (country_code,))
            
            # Fetch the result (expecting one row of results)
            result = cursor.fetchone()

            if result:
                resources = {
                    'CountryCode': result[0],
                    'RiverTotal': result[1],
                    'LakeTotal': result[2],
                    'MountainTotal': result[3],
                    'IslandTotal': result[4]
                }
                return render_template('country_resources.html', resources=[resources])
            else:
                return render_template('country_resources.html', resources=None)

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return render_template('country_resources.html', resources=None)
        finally:
            cursor.close()
            conn.close()
    else:
        return redirect(url_for('routes.login'))

# Display the list of countries and their GDP Per Capita
@routes.route('/country/gdp')
def country_gdp():
    if 'email' in session:
        if session['role'] == 'continent':
            return redirect(url_for('routes.home'))
        
        # Get the current page number from the query string (default to page 1)
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of items per page
        
        # Calculate the starting row for the query (offset)
        offset = (page - 1) * per_page
        
        # Get a connection to the database
        conn = create_connection()
        
        if conn:
            # Create a cursor from the connection
            cursor = conn.cursor()
            
            # Execute a query with pagination using OFFSET and FETCH NEXT
            cursor.execute('''
                SELECT Code, Name, Capital, FORMAT(Population, 'N0') AS Population, FORMAT(dbo.udf_CountryGDPPerCapita(Code), 'N6') GDPPerCapita
                FROM country
                ORDER BY GDPPerCapita DESC  -- or any other column for sorting
                OFFSET ? ROWS
                FETCH NEXT ? ROWS ONLY
            ''', (offset, per_page))
            
            # Fetch the results
            countries = cursor.fetchall()
            
            # Get the total count of rows to calculate the number of pages
            cursor.execute('SELECT COUNT(*) FROM Country')
            total_count = cursor.fetchone()[0]
            
            # Close the cursor and connection
            cursor.close()
            conn.close()
            
            # Calculate total number of pages
            total_pages = (total_count + per_page - 1) // per_page
            
            # Pass the results, total pages, and current page to the template
            return render_template('country_gdp.html', countries=countries, total_pages=total_pages, current_page=page)
        else:
            return render_template('country_gdp.html', countries=None)
    else:
        return redirect(url_for('routes.login'))