# lender.py
class Lender:
    def __init__(self, name, interest_rate):
        self.name = name
        self.interest_rate = interest_rate

    def calculate_interest(self, amount):
        return round(amount * self.interest_rate, 2)
