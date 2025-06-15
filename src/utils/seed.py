from faker import Faker
import random

fake = Faker('id_ID')

class Seeder:
    def __init__(self):
        self.name = "aku gatau konstruktor harus ada apa engga jd aku kasi ginian"

    def generate_first_name():
        return fake.first_name()

    def generate_last_name():
        return fake.last_name()

    def generate_phone_number():
        return fake.phone_number()

    def generate_dob():
        return fake.date_of_birth(minimum_age=20, maximum_age=50).strftime('%Y-%m-%d')

    def generate_address():
        provinsi = fake.state()
        kota = fake.city()
        jalan = fake.street_address()
        return f"{jalan}, {kota}, {provinsi}"

    def generate_data(self, num: int):
        data = []
        for _ in range(num):
            profile = {
                'first_name': self.generate_first_name(),
                'last_name': self.generate_last_name(),
                'phone_number': self.generate_phone_number(),
                'dob': self.generate_dob(),
                'address': self.generate_address()
            }
            data.append(profile)
        return data