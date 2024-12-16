USE BISMILLAH_PROJECT;
-- untuk nyimpen akun yang login 
CREATE TABLE users (
    username VARCHAR(10) PRIMARY KEY,
    password NVARCHAR(8),
    email VARCHAR(50) UNIQUE 
    FOREIGN KEY (email) REFERENCES email_role(email)
);