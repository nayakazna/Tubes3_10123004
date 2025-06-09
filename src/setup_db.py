# setup_db.py
import mysql.connector
from mysql.connector import Error
import getpass
import os

def setup_database():
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