from django.test import TestCase

# Create your tests here.
import requests
import time 


def runtime(func):
    """
    A decorator to check the runtime of the function

    Args:
        func: function to be executed

    Return:
        wrapper: function to be executed

    """
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Time taken: {end - start}")
        return result
    return wrapper


# @runtime
def register():
    data = {
    "username" : "Username",
    "email" : "useremail@gmail.com",
    "phone" : 9025993439493,
    "password" : "this is the password",
    "first_name": "first name",
    "last_name": "last name",
    "company" : "company",
}

    url = "http://127.0.0.1:8000/auth/register"

    response = requests.post(url, data=data)
    return response.text


@runtime
def login():
    data = {"email": "wlfskd@gmail.com",
            "amount": 2000}
    
    # url = "https://fasticket.onrender.com/auth/login"
    url = "http://127.0.0.1:8000/auth/login"
    response = requests.post(url, data=data)
    return response.text


# @runtime
class Payment:
    
    def initialize():
        email = "useremail@gmail.com"
        amount = 3000
        body = {
            "email" : email,
            "amount": amount,
        }
        url = "http://127.0.0.1:8000/payments/initiate_payment/"
        response = requests.post(url, data=body)
        return response.json()



print(Payment.initialize())