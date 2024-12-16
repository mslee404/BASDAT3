import logging
import sys
from connect import create_connection
from tabulate import tabulate

# Configure logging to console
logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    format='%(levelname)s: %(message)s',
    level=logging.DEBUG
)

# Establish a database connection
conn = create_connection()

if conn:
    cursor = conn.cursor()
    
    # Retrieve the top 3 countries by population
    cursor.execute('SELECT TOP 5 nconst FROM fix_primaryprofession')
    
    # Define headers
    headers = ["Name ID"]
    
    # Fetch all rows and display with tabulate
    rows = cursor.fetchall()
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    # Close cursor and connection
    cursor.close()
    conn.close()

else:
    logger.error('Failed to connect to the SQL Server database.')