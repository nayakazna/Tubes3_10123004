import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'ats_db'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', '')
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Successfully connected to MySQL database")
                return True
                
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
            return False
    
    def fetch_all(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Error as e:
            print(f"Error fetching data: {e}")
            return None
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection closed")
    
    def create_tables(self):
        # Create ApplicantProfile table
        create_applicant_profile = """
        CREATE TABLE IF NOT EXISTS ApplicantProfile (
            applicant_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) DEFAULT NULL,
            last_name VARCHAR(50) DEFAULT NULL,
            date_of_birth DATE DEFAULT NULL,
            address VARCHAR(255) DEFAULT NULL,
            phone_number varchar(100) DEFAULT NULL)
        """
        
        # Create ApplicationDetail table
        create_application_detail = """
        CREATE TABLE IF NOT EXISTS ApplicationDetail (
            detail_id INT AUTO_INCREMENT PRIMARY KEY,
            applicant_id INT NOT NULL,
            application_role VARCHAR(100) DEFAULT NULL,
            cv_path TEXT,
            FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id)
        )
        """
        
        self.execute_query(create_applicant_profile)
        self.execute_query(create_application_detail)
        print("Tables created successfully")