from database.connection import DatabaseConnection
from encryption.custom_encryption import CustomEncryption
from datetime import datetime

class ApplicantModel:
    def __init__(self):
        self.db = DatabaseConnection()
        self.encryption = CustomEncryption()
        self.db.connect()
        self.db.create_tables()
    
    def create_applicant(self, first_name, last_name, date_of_birth=None, address=None, phone_number=None):
        """Create new applicant with encrypted data"""
        # Encrypt sensitive data
        encrypted_data = self.encryption.encrypt_profile_data({
            'first_name': first_name,
            'last_name': last_name,
            'address': address,
            'phone_number': phone_number
        })
        
        query = """
        INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        params = (
            encrypted_data['first_name'],
            encrypted_data['last_name'],
            date_of_birth,
            encrypted_data['address'],
            encrypted_data['phone_number']
        )
        
        self.db.execute_query(query, params)
        
        # Get the last inserted ID
        return self.db.cursor.lastrowid
    
    def get_applicant(self, applicant_id):
        """Get applicant by ID and decrypt data"""
        query = "SELECT * FROM ApplicantProfile WHERE applicant_id = %s"
        result = self.db.fetch_one(query, (applicant_id,))
        
        if result:
            # Decrypt sensitive data
            decrypted_result = self.encryption.decrypt_profile_data(result)
            return decrypted_result
        
        return None
    
    def get_all_applicants(self):
        """Get all applicants with decrypted data"""
        query = "SELECT * FROM ApplicantProfile"
        results = self.db.fetch_all(query)
        
        # Decrypt all results
        decrypted_results = []
        for result in results:
            decrypted_results.append(self.encryption.decrypt_profile_data(result))
        
        return decrypted_results
    
    def update_applicant(self, applicant_id, **kwargs):
        """Update applicant information"""
        # Filter out None values
        updates = {k: v for k, v in kwargs.items() if v is not None}
        
        if not updates:
            return False
        
        # Encrypt sensitive fields
        if any(field in updates for field in ['first_name', 'last_name', 'address', 'phone_number']):
            updates = self.encryption.encrypt_profile_data(updates)
        
        # Build update query
        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        query = f"UPDATE ApplicantProfile SET {set_clause} WHERE applicant_id = %s"
        
        params = list(updates.values()) + [applicant_id]
        
        return self.db.execute_query(query, params)
    
    def delete_applicant(self, applicant_id):
        """Delete applicant and all related applications"""
        # First delete related applications
        self.db.execute_query("DELETE FROM ApplicationDetail WHERE applicant_id = %s", (applicant_id,))
        
        # Then delete applicant
        query = "DELETE FROM ApplicantProfile WHERE applicant_id = %s"
        return self.db.execute_query(query, (applicant_id,))
    
    def close(self):
        """Close database connection"""
        self.db.close()


class ApplicationModel:
    def __init__(self):
        self.db = DatabaseConnection()
        self.db.connect()
    
    def create_application(self, applicant_id, application_role, cv_path):
        """Create new application"""
        query = """
        INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path)
        VALUES (%s, %s, %s)
        """
        
        params = (applicant_id, application_role, cv_path)
        self.db.execute_query(query, params)
        
        return self.db.cursor.lastrowid
    
    def get_application(self, detail_id):
        """Get application by ID"""
        query = "SELECT * FROM ApplicationDetail WHERE detail_id = %s"
        return self.db.fetch_one(query, (detail_id,))
    
    def get_applications_by_applicant(self, applicant_id):
        """Get all applications for an applicant"""
        query = "SELECT * FROM ApplicationDetail WHERE applicant_id = %s"
        return self.db.fetch_all(query, (applicant_id,))
    
    def get_all_applications_with_applicants(self):
        """Get all applications with applicant information"""
        query = """
        SELECT 
            ad.*,
            ap.first_name,
            ap.last_name,
            ap.date_of_birth,
            ap.address,
            ap.phone_number
        FROM ApplicationDetail ad
        JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id
        """
        
        results = self.db.fetch_all(query)
        
        # Decrypt applicant data
        encryption = CustomEncryption()
        for result in results:
            decrypted_data = encryption.decrypt_profile_data({
                'first_name': result['first_name'],
                'last_name': result['last_name'],
                'address': result['address'],
                'phone_number': result['phone_number']
            })
            result.update(decrypted_data)
        
        return results
    
    def update_application(self, detail_id, **kwargs):
        """Update application information"""
        updates = {k: v for k, v in kwargs.items() if v is not None}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        query = f"UPDATE ApplicationDetail SET {set_clause} WHERE detail_id = %s"
        
        params = list(updates.values()) + [detail_id]
        
        return self.db.execute_query(query, params)
    
    def delete_application(self, detail_id):
        """Delete application"""
        query = "DELETE FROM ApplicationDetail WHERE detail_id = %s"
        return self.db.execute_query(query, (detail_id,))
    
    def close(self):
        """Close database connection"""
        self.db.close()