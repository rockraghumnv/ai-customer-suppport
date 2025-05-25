from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Company

class APISmokeTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.username = "apitestuser"
        self.password = "apitestpass"
        # Register user
        resp = self.client.post(reverse('register'), {"username": self.username, "password": self.password}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.token = resp.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        # Create company
        self.company_data = {
            "name": "Test Company",
            "domain": "testcompany.com",
            "company_email": "test@testcompany.com",
            "business_type": "IT"
        }
        resp = self.client.post(reverse('company-list-create'), self.company_data, format='json')
        self.assertIn(resp.status_code, [200, 201])
        self.company_id = resp.data['id']

    def test_endpoints(self):
        # Company list
        resp = self.client.get(reverse('company-list-create'))
        print('GET /companies/', resp.status_code)
        self.assertEqual(resp.status_code, 200)
        # Company detail
        resp = self.client.get(reverse('company-detail', args=[self.company_id]))
        print('GET /companies/<id>/', resp.status_code)
        self.assertEqual(resp.status_code, 200)
        # Product CRUD
        prod_data = {"company": self.company_id, "name": "Test Product", "description": "desc"}
        resp = self.client.post(reverse('product-list-create'), prod_data, format='json')
        print('POST /products/', resp.status_code)
        self.assertIn(resp.status_code, [200, 201])
        prod_id = resp.data['id']
        resp = self.client.get(reverse('product-detail', args=[prod_id]))
        print('GET /products/<id>/', resp.status_code)
        self.assertEqual(resp.status_code, 200)
        # Service CRUD
        serv_data = {"company": self.company_id, "name": "Test Service", "description": "desc"}
        resp = self.client.post(reverse('service-list-create'), serv_data, format='json')
        print('POST /services/', resp.status_code)
        self.assertIn(resp.status_code, [200, 201])
        serv_id = resp.data['id']
        resp = self.client.get(reverse('service-detail', args=[serv_id]))
        print('GET /services/<id>/', resp.status_code)
        self.assertEqual(resp.status_code, 200)
        # Ticket CRUD
        ticket_data = {"company": self.company_id, "user_email": "user@test.com", "subject": "Test Ticket", "description": "desc"}
        resp = self.client.post(reverse('ticket-list-create'), ticket_data, format='json')
        print('POST /tickets/', resp.status_code)
        self.assertIn(resp.status_code, [200, 201])
        ticket_id = resp.data['id']
        resp = self.client.get(reverse('ticket-detail', args=[ticket_id]))
        print('GET /tickets/<id>/', resp.status_code)
        self.assertEqual(resp.status_code, 200)
        # Feedback
        feedback_data = {"company": self.company_id, "user_email": "user@test.com", "rating": 5, "comment": "Great!"}
        resp = self.client.post(reverse('feedback'), feedback_data, format='json')
        print('POST /feedback/', resp.status_code)
        self.assertIn(resp.status_code, [200, 201])
        resp = self.client.get(reverse('feedback-list'))
        print('GET /feedback-list/', resp.status_code)
        self.assertEqual(resp.status_code, 200)
        # Chatbot (text only, no image)
        chatbot_data = {"query": "What is your refund policy?", "company": "testcompany.com", "user_email": "user@test.com"}
        resp = self.client.post(reverse('chatbot-interaction'), chatbot_data, format='multipart')
        print('POST /chatbot/', resp.status_code)
        self.assertIn(resp.status_code, [200, 201, 500])  # 500 if Gemini not configured
        # Copilot summary (should work if ticket exists)
        resp = self.client.get(reverse('copilot-summary', args=[ticket_id]))
        print('GET /copilot-summary/<ticket_id>/', resp.status_code)
        self.assertIn(resp.status_code, [200, 404, 500])

class APIEdgeCaseTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.username = "edgeuser"
        self.password = "edgepass"
        resp = self.client.post(reverse('register'), {"username": self.username, "password": self.password}, format='json')
        self.token = resp.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        self.company_data = {
            "name": "Edge Company",
            "domain": "edgecompany.com",
            "company_email": "edge@edgecompany.com",
            "business_type": "IT"
        }
        resp = self.client.post(reverse('company-list-create'), self.company_data, format='json')
        self.company_id = resp.data['id']

    def test_unauthorized_access(self):
        # Remove credentials
        self.client.credentials()
        resp = self.client.get(reverse('company-list-create'))
        self.assertEqual(resp.status_code, 401)
        # Try with invalid token
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken')
        resp = self.client.get(reverse('company-list-create'))
        self.assertEqual(resp.status_code, 401)

    def test_invalid_input(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        # Missing required fields
        resp = self.client.post(reverse('company-list-create'), {}, format='json')
        self.assertEqual(resp.status_code, 400)
        # Invalid email
        bad_data = self.company_data.copy()
        bad_data['company_email'] = 'notanemail'
        resp = self.client.post(reverse('company-list-create'), bad_data, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_duplicate_entries(self):
        # Duplicate company
        resp = self.client.post(reverse('company-list-create'), self.company_data, format='json')
        self.assertIn(resp.status_code, [400, 409])
        # Duplicate product
        prod_data = {"company": self.company_id, "name": "Dup Product", "description": "desc"}
        resp = self.client.post(reverse('product-list-create'), prod_data, format='json')
        self.assertIn(resp.status_code, [200, 201])
        resp = self.client.post(reverse('product-list-create'), prod_data, format='json')
        self.assertIn(resp.status_code, [400, 409])

    def test_file_upload_errors(self):
        # Upload with no file
        resp = self.client.post(reverse('file-upload'), {}, format='multipart')
        self.assertEqual(resp.status_code, 400)
        # Upload with bad file type
        from io import BytesIO
        bad_file = BytesIO(b"notarealfile")
        bad_file.name = 'badfile.exe'
        resp = self.client.post(reverse('file-upload'), {"file": bad_file, "company": self.company_id}, format='multipart')
        self.assertEqual(resp.status_code, 400)
        # Upload oversized file (simulate >10MB)
        big_file = BytesIO(b"0" * 11 * 1024 * 1024)
        big_file.name = 'bigfile.txt'
        resp = self.client.post(reverse('file-upload'), {"file": big_file, "company": self.company_id}, format='multipart')
        self.assertIn(resp.status_code, [400, 413])

    def test_ai_endpoint_errors(self):
        # Chatbot with missing company
        chatbot_data = {"query": "Hi", "company": "notareal.com", "user_email": "user@x.com"}
        resp = self.client.post(reverse('chatbot-interaction'), chatbot_data, format='multipart')
        self.assertIn(resp.status_code, [400, 404, 500])
        # Chatbot with missing query
        chatbot_data = {"company": "edgecompany.com", "user_email": "user@x.com"}
        resp = self.client.post(reverse('chatbot-interaction'), chatbot_data, format='multipart')
        self.assertEqual(resp.status_code, 400)
        # Copilot summary with bad ticket id
        resp = self.client.get(reverse('copilot-summary', args=[999999]))
        self.assertIn(resp.status_code, [404, 400])

    def test_admin_kb_doc_management_edge_cases(self):
        # Try to delete non-existent KB doc
        resp = self.client.delete(reverse('uploadedfile-detail', args=[999999]))
        self.assertIn(resp.status_code, [404, 400, 403])
        # Try to update KB doc with invalid data
        resp = self.client.patch(reverse('uploadedfile-detail', args=[999999]), {"is_active": "notabool"}, format='json')
        self.assertIn(resp.status_code, [404, 400, 403])
