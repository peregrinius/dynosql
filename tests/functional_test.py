#!env/bin/python3
import unittest
import sys

import dyno

class FunctionalTestCase(unittest.TestCase):

    def setUp(self):
        self.dyno = dyno.Dyno()
        self.tables = {}

    def tearDown(self):
        for k in list(self.tables):
            del self.tables[k]

    def test_create_table(self):
        self.tables['music'] = self.dyno(table_name='music', partition_key=('artist', 'str',), sort_key=('song', 'str',))
        self.assertEqual(self.tables['music'].describe['Table']['TableName'], 'music')

    def test_delete_table(self):
        self.tables['music'] = self.dyno(table_name='music', partition_key=('artist', 'str',), sort_key=('song', 'str',))
        del self.tables['music']
        self.assertNotIn('music1', self.dyno.keys())

    def test_insert_record_in_table_with_sort_key(self):
        self.tables['music'] = self.dyno(table_name='music', partition_key=('artist', 'str',), sort_key=('song', 'str',))
        self.tables['music']['Prince', 'Purple Rain'] = {'released': 1984, 'album': 'Purple Rain'}
        self.assertEqual(self.tables['music']['Prince', 'Purple Rain']['released'], 1984)

    def test_insert_record_in_table_without_sort_key(self):
        self.tables['music'] = self.dyno(table_name='music', partition_key=('artist', 'str',))
        self.tables['music']['Prince - Purple Rain'] = {'released': 1984, 'album': 'Purple Rain'}
        self.assertEqual(self.tables['music']['Prince - Purple Rain']['released'], 1984)



if __name__ == '__main__':
    unittest.main()