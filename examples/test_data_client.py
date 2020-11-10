# coding: utf-8

from archappl.client import ArchiverDataClient
import unittest


class TestArchiverDataClient(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_client(self):
        client = ArchiverDataClient()
        self.assertEqual(str(client), 
                '[Data Client] Archiver Appliance on: http://127.0.0.1:17665/retrieval/data/getData.json')
        self.assertEqual(client.url,
                'http://127.0.0.1:17665/retrieval/data/getData.json')
        self.assertEqual(client.format, 'json')

        client.format = 'csv'
        self.assertEqual(client.url,
                'http://127.0.0.1:17665/retrieval/data/getData.csv')

        client.url = 'http://192.168.0.100'
        self.assertEqual(client.url,
                'http://192.168.0.100/retrieval/data/getData.csv')
