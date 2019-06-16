import unittest
import struct

class Test_test1(unittest.TestCase):
    def test_A(self):
        self.assertEqual(1, 1)
        #self.fail("Not implemented")

    def test_A2(self): 
        speed = 1000
        speedInBytes = bytes(struct.pack('>h', 1500))
        print('{} {}'.format(speedInBytes[0], speedInBytes[1]))
        self.assertEqual(1, 1)
        #self.fail("Not implemented")  

if __name__ == '__main__':
    unittest.main()
