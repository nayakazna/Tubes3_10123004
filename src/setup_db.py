# setup_db.py
import mysql.connector
from mysql.connector import Error
import getpass
import os
import sys
import re
from encryption.custom_encryption import CustomEncryption

def setup_database():
    conn = None
    cursor = None
    app_conn = None
    app_cursor = None
    try:
        # input kredensial MySQL
        root_user = input("Masukkan username MySQL (tekan Enter untuk 'root'): ") or 'root'
        root_password = getpass.getpass(f"Masukkan password untuk {root_user}: ")

        print("Menyambungkan ke MySQL...")
        conn = mysql.connector.connect(
            host='localhost',
            user=root_user,
            password=root_password
        )

        cursor = conn.cursor()
        print("\x1b[32mBerhasil terhubung ke server MySQL.\x1b[0m")

        # bikin database dan username
        db_name = 'ats_db'
        app_user = 'cvmagang'
        app_password = 'AkuSukaIndomie123!' 

        print(f"\nMembuat database '{db_name}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET UTF8MB4;")
        
        print(f"Membuat user '{app_user}'...")
        try:
            cursor.execute(f"CREATE USER '{app_user}'@'localhost' IDENTIFIED BY '{app_password}';")
        except Error as e:
            if e.errno == 1396:
                print(f"   - User '{app_user}' sudah ada.")
            else:
                raise
        cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{app_user}'@'localhost';")
        cursor.execute("FLUSH PRIVILEGES;")

        cursor.close()
        conn.close()

        # seeding pake enkripsi
        print("\nSeeding...")

        app_conn = mysql.connector.connect(
            host='localhost',
            database=db_name,
            user=app_user,
            password=app_password
        )
        app_cursor = app_conn.cursor()

        with open('src/tubes3_seeding.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        print("Membuat tabel ApplicantProfile dan ApplicationDetail...")
        create_table_statements = re.findall(r'CREATE TABLE.*?;', sql_script, re.DOTALL)
        for stmt in create_table_statements:
            app_cursor.execute(stmt)
        print("\x1b[32mTabel berhasil dibuat.\x1b[0m")

        print("Memproses dan mengenkripsi data ApplicantProfile...")
        encryption = CustomEncryption()
        profile_inserts = re.findall(r"\((\d+),\s*'([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)'\)", sql_script)
        
        insert_profile_query = """
        INSERT INTO ApplicantProfile (applicant_id, first_name, last_name, date_of_birth, address, phone_number) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        for row in profile_inserts:
            applicant_id, first_name, last_name, dob, address, phone = row
            
            # Enkripsi data yang perlu dienkripsi
            encrypted_first_name = encryption.encrypt(first_name)
            encrypted_last_name = encryption.encrypt(last_name)
            encrypted_address = encryption.encrypt(address)
            encrypted_phone = encryption.encrypt(phone)
            
            # Masukkan data yang sudah terenkripsi
            app_cursor.execute(insert_profile_query, (
                applicant_id, encrypted_first_name, encrypted_last_name, dob, encrypted_address, encrypted_phone
            ))
        print(f"\x1b[32m{len(profile_inserts)} baris data ApplicantProfile berhasil dimasukkan dan dienkripsi.\x1b[0m")

        print("Memproses data ApplicationDetail...")
        
        # Regex untuk mengekstrak nilai dari INSERT INTO ApplicationDetail
        detail_inserts = re.findall(r"\((\d+),\s*(\d+),\s*(?:'([^']*)'|NULL),\s*'([^']*)'\)", sql_script)

        insert_detail_query = """
        INSERT INTO ApplicationDetail (detail_id, applicant_id, application_role, cv_path) 
        VALUES (%s, %s, %s, %s)
        """
        for row in detail_inserts:
            detail_id, applicant_id, role, path = row
            # Jika role adalah string kosong dari regex, ubah jadi None untuk NULL di SQL
            app_cursor.execute(insert_detail_query, (detail_id, applicant_id, role or None, path))
        
        print(f"\x1b[32m{len(detail_inserts)} baris data ApplicationDetail berhasil dimasukkan.\x1b[0m")

        app_conn.commit()
        
        # bikin file .env
        print("Membikin file .env...")
        
        env_content = f"""DB_HOST=localhost
DB_NAME={db_name}
DB_USER={app_user}
DB_PASSWORD={app_password}
"""
        with open('.env', 'w') as f:
            f.write(env_content)
            
        print("\x1b[32mfile .env berhasil dibikin.\x1b[0m")

        print("\n\x1b[32mBang done bang\x1b[0m")
    except Error as e:
        print(f"\n\x1b[31mError: {e}\x1b[0m")
        print("\x1b[31mPastikan server MySQL sedang berjalan atau username/passwordnya bener\x1b[0m")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_database()