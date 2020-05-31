#!/usr/bin/env python
"""
api tests

these tests use the requests package however similar requests can be made with curl

e.g.

data = '{"key":"value"}'
curl -X POST -H "Content-Type: application/json" -d "%s" http://localhost:8080/predict'%(data)
"""

import sys
import os
import unittest
import requests
import re
from ast import literal_eval
import numpy as np
from datetime import date

port = 8080

try:
    requests.post('http://0.0.0.0:{}/predict'.format(port))
    server_available = True
except:
    server_available = False
    
## test class for the main window function
class ApiTest(unittest.TestCase):
    """
    test the essential functionality
    """
    
    @unittest.skipUnless(server_available,"local server is not running")
    def test_predict_empty(self):
        """
        ensure appropriate failure types
        """
    
        ## provide no data at all 
        r = requests.post('http://0.0.0.0:{}/predict'.format(port))
        self.assertEqual(re.sub('\n|"','',r.text),"[]")

        ## provide improperly formatted data
        r = requests.post('http://0.0.0.0:{}/predict'.format(port),json={"key":"value"})     
        self.assertEqual(re.sub('\n|"','',r.text),"[]")
    
    @unittest.skipUnless(server_available,"local server is not running")
    def test_predict(self):
        """
        test the predict functionality
        """
      
        query_data = np.array([[6.1,2.8]])
        query_data = query_data.tolist()
        query_type = 'numpy'
        request_json = {'query':query_data,'type':query_type}

        r = requests.post('http://0.0.0.0:{}/predict'.format(port),json=request_json)

        response = literal_eval(r.text)
        self.assertEqual(response['y_pred'],[1])

    @unittest.skipUnless(server_available,"local server is not running")
    def test_train(self):
        """
        test the predict functionality
        """
      
        request_json = {'mode':'test'}
        r = requests.post('http://0.0.0.0:{}/train'.format(port),json=request_json)
        train_complete = re.sub("\W+","",r.text)
        self.assertEqual(train_complete,'true')

    @unittest.skipUnless(server_available,"local server is not running")
    def test_logs_api(self):

        # Generate log entry
        today = date.today()
        year = today.year
        month = today.month

        try:
            r_train = requests.get(f'http://0.0.0.0:{port}/logs/train/{year}/{month}', stream=True)
            r_pred = requests.get(f'http://0.0.0.0:{port}/logs/pred/{year}/{month}', stream=True)
        except requests.exceptions.HTTPError:
            self.fail("HTTP Error")

        try:
            r_train_first_line = next(r_train.iter_lines()).decode('ascii')
            r_pred_first_line = next(r_pred.iter_lines()).decode('ascii')
        except StopIteration:
            self.fail("No log returned")

        self.assertRegex(r_train_first_line, "^unique_id")
        self.assertRegex(r_pred_first_line, "^unique_id")

### Run the tests
if __name__ == '__main__':
    unittest.main()
