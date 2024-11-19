from django.test import TestCase
import requests

class LiveURLTest(TestCase):

    def test_live_urls(self):
        # List of URLs to check, replace with your URLs
        urls = [
            'https://www.google.com/',
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.check_url(url)
                self.assertEqual(response.status_code, 200, f'URL {url} returned a {response.status_code} status code.')

    def check_url(self, url):
        try:
            # Send a GET request to the URL
            response = requests.get(url)
            return response
        except requests.exceptions.RequestException as e:
            self.fail(f'Error while checking URL {url}: {str(e)}')