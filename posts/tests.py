from django.test import TestCase, Client


class Test404(TestCase):
    def test_returning_404(self):
        self.client=Client()
        response=self.client.get('nonexistantpage')
        self.assertEqual(response.status_code, 404)
# Create your tests here.
