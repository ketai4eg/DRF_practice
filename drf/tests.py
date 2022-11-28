from django.test import TestCase
from rest_framework import status
from django.contrib import auth
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from .models import Transactions, Categories, Balance


def user_creation(self, data=None):
    if data is None:
        data = {
            'username': ['M'],
            'email': ['m@m.m'],
            'password': ['m'],
        }
    self.client.post('/user_create/', data=data)
    del data['email']
    token = self.client.post('/token/', data=data)
    return token.data['token']


class ApiRootTest(TestCase):
    def test_url_root(self):
        response = self.client.get('')
        self.assertTrue(status.is_success(response.status_code))


class UserApiTest(TestCase):
    def test_creation_of_new_user(self):
        response = self.client.post('/user_create/', data={
            'username': ['Max'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        self.assertTrue(response.status_code == 200)

    def test_user_information_correct(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        response = self.client.get('/user_info/', content_type='application/json', **headers)
        self.assertTrue(response.data['results'][0]['username'] == 'Test1' and response.status_code == 200)

    def test_user_token_incorrect(self):
        token = user_creation(self)
        headers = {"HTTP_AUTHORIZATION": f"Token {token}0"}
        response = self.client.get('/user_info/', content_type='application/json', **headers)
        print(response)
        self.assertTrue(response.status_code == 403)

    def test_balance_top_up(self):
        token = user_creation(self, data={
            "username": ["Mx"],
            "email": ["mx@max.max"],
            "password": ["mx"],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        data = {
            "balance": 50,
        }
        response = self.client.put('/user_info/', content_type='application/json', data=data, **headers)
        self.assertTrue(response.status_code == 200 and response.data['balance'] == 50)

    def test_balance_top_up_wrong_token(self):
        token = user_creation(self, data={
            "username": ["Mx"],
            "email": ["mx@max.max"],
            "password": ["mx"],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token {token}0"}
        data = {
            "balance": 50,
        }
        response = self.client.put('/user_info/', content_type='application/json', data=data, **headers)
        self.assertTrue(response.status_code == 403)


class CategoriesApiTest(TestCase):
    def test_get_categories_list(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        response = self.client.get('/categories/', content_type='application/json', **headers)
        self.assertTrue(response.data['count'] == 11 and response.status_code == 200)

    def test_get_categories_list_without_token(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token "}
        response = self.client.get('/categories/', content_type='application/json', **headers)
        self.assertTrue(response.status_code == 403)

    def test_create_new_category(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        data = {
            "category_list": "alcohol",
        }
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        response = self.client.post('/categories/', content_type='application/json', data=data, **headers)
        self.assertTrue(response.data['category_list'] == "alcohol" and response.status_code == 201)

    def test_create_new_category_without_token(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        data = {
            "category_list": "alcohol",
        }
        headers = {"HTTP_AUTHORIZATION": f"Token "}
        response = self.client.post('/categories/', content_type='application/json', data=data, **headers)
        self.assertTrue(response.status_code == 403)

    def test_update_category(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        data = {
            "category_list": "alcohol",
        }
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        cat_id = self.client.post('/categories/', content_type='application/json', data=data, **headers).data['id']
        new_data = {
            "category_list": "alcohol and girls",
        }
        response = self.client.put(f'/categories/{cat_id}/', content_type='application/json', data=new_data, **headers)
        self.assertTrue(response.data['category_list'] == "alcohol and girls" and response.status_code == 200)

    def test_update_category_without_token(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        data = {
            "category_list": "alcohol",
        }
        headers = {"HTTP_AUTHORIZATION": f"Token "}
        response = self.client.post('/categories/', content_type='application/json', data=data, **headers)
        new_data = {
            "category_list": "alcohol and girls",
        }
        self.assertTrue(response.status_code == 403)

    def test_delete_category(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        data = {
            "category_list": "alcohol",
        }
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        cat_id = self.client.post('/categories/', content_type='application/json', data=data, **headers).data['id']
        response = self.client.delete(f'/categories/{cat_id}/', content_type='application/json', **headers)
        self.assertTrue(response.status_code == 204)

    def test_delete_category_without_token(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        data = {
            "category_list": "alcohol",
        }
        headers = {"HTTP_AUTHORIZATION": f"Token "}
        response = self.client.post('/categories/', content_type='application/json', data=data, **headers)
        self.assertTrue(response.status_code == 403)


class TransactionsApiTest(TestCase):
    def test_get_new_transaction(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        data = {
            "amount": 20,
            "category": "alcohol",
            "organisation": "Berezka"
        }
        response = self.client.post('/transactions/', content_type='application/json', data=data, **headers)
        self.assertTrue(response.data["amount"] == 20 and response.status_code == 201)

    def test_get_new_transaction_without_token(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token "}
        data = {
            "amount": 20,
            "category": "alcohol",
            "organisation": "Berezka"
        }
        response = self.client.post('/transactions/', content_type='application/json', data=data, **headers)
        self.assertTrue(response.status_code == 403)

    def test_get_transactions_list(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        data = {
            "amount": 20,
            "category": "alcohol",
            "organisation": "Berezka"
        }
        self.client.post('/transactions/', content_type='application/json', data=data, **headers)
        response = self.client.get('/transactions/', content_type='application/json', **headers)
        self.assertTrue(response.data['count'] == 1 and response.status_code == 200)

    def test_get_transactions_list_without_token(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token "}
        data = {
            "amount": 20,
            "category": "alcohol",
            "organisation": "Berezka"
        }
        self.client.post('/transactions/', content_type='application/json', data=data, **headers)
        response = self.client.get('/transactions/', content_type='application/json', **headers)
        self.assertTrue(response.status_code == 403)

    def test_update_transaction(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        data = {
            "amount": 20,
            "category": "alcohol",
            "organisation": "Berezka"
        }
        trans_id = self.client.post('/transactions/', content_type='application/json', data=data, **headers).data['id']
        new_data = {
            "amount": 50,
            "category": "alcohol",
            "organisation": "Berezka"
        }
        response = self.client.put(f'/transactions/{trans_id}/', content_type='application/json', data=new_data,
                                   **headers)
        self.assertTrue(response.data["amount"] == 50 and response.status_code == 200)

    def test_update_transaction_without_token(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token "}
        data = {
            "amount": 20,
            "category": "alcohol",
            "organisation": "Berezka"
        }
        response = self.client.post('/transactions/', content_type='application/json', data=data, **headers)
        new_data = {
            "amount": 50,
            "category": "alcohol",
            "organisation": "Berezka"
        }
        self.assertTrue(response.status_code == 403)

    def test_delete_transaction(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token {token}"}
        data = {
            "amount": 20,
            "category": "alcohol",
            "organisation": "Berezka"
        }
        trans_id = self.client.post('/transactions/', content_type='application/json', data=data, **headers).data['id']
        response = self.client.delete(f'/transactions/{trans_id}/', content_type='application/json', **headers)
        self.assertTrue(response.status_code == 204)

    def test_delete_transaction_without_token(self):
        token = user_creation(self, data={
            'username': ['Test1'],
            'email': ['max@max.max'],
            'password': ['max'],
        })
        headers = {"HTTP_AUTHORIZATION": f"Token "}
        data = {
            "amount": 20,
            "category": "alcohol",
            "organisation": "Berezka"
        }
        response = self.client.post('/transactions/', content_type='application/json', data=data, **headers)
        self.assertTrue(response.status_code == 403)
