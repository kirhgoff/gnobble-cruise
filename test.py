import unittest
import datetime
import time

class GnobbleTestCase(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
    def testInMircoseconds(self):
        value = datetime.datetime.now ()
        micro = time.mktime(value.timetuple())+1e-6*value.microsecond
        print micro
        pass
        
if __name__ == '__main__':
    unittest.main()