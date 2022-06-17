from django.test import TestCase


class ViewTestClass(TestCase):
    def test_404_error_page(self):
        response = self.client.get('/nonexist-page/')

        self.assertEquals(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
