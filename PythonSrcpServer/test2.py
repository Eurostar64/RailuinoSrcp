import unittest
import controlstation
import controlstationSimulated

class TestHelperInfoCB:
    def enqueue(self, code, codeMsg, Msg):
        self.infocbs.append((code, codeMsg, Msg))

    def compareLastWith(self, code, codeMsg, Msg):
        (code2, codeMsg2, Msg2) = self.infocbs[len(self.infocbs)-1]
        return code2 == code and codeMsg2 == codeMsg and Msg2 == Msg


    def __init__(self):
        self.infocbs = []


class Test_test2(unittest.TestCase):
   
    def test_Simulated_Init(self):
        cs = controlstationSimulated.controlstationSimulated()
        thInfoCb = TestHelperInfoCB()
        cs.infocb = thInfoCb.enqueue

        self.assertEqual(1, cs.GA_INIT(15, 'N'))
        self.assertEqual(0, cs.GA_INIT(15, 'N'))
        self.assertEqual(1, cs.GL_INIT(18, 'N',2,14,5))
        self.assertEqual(0, cs.GL_INIT(18, 'N',2,14,5))

    def test_Simulated_Power(self):
        cs = controlstationSimulated.controlstationSimulated()
        thInfoCb = TestHelperInfoCB()
        cs.infocb = thInfoCb.enqueue

        self.assertEqual(1, cs.POWER_SET(1))
        self.assertTrue(thInfoCb.compareLastWith(101, "INFO", "1 POWER ON"))

        self.assertEqual(1, cs.POWER_SET(0))
        self.assertTrue(thInfoCb.compareLastWith(101, "INFO", "1 POWER OFF"))

    def test_Simulated_GA_SET(self):
        cs = controlstationSimulated.controlstationSimulated()
        thInfoCb = TestHelperInfoCB()
        cs.infocb = thInfoCb.enqueue

        self.assertEqual(1, cs.GA_INIT(15, 'N'))
        self.assertTrue(thInfoCb.compareLastWith(101, "INFO", "1 GA 15 N"))

        self.assertEqual(1, cs.GA_SET(15, 1, 300))
        self.assertTrue(thInfoCb.compareLastWith(100, "INFO", "1 GA 15 1 1"))

        self.assertEqual(1, cs.GA_SET(15, 0, 300))
        self.assertTrue(thInfoCb.compareLastWith(100, "INFO", "1 GA 15 0 1"))

    def test_Simulated_GL(self):
        cs = controlstationSimulated.controlstationSimulated()
        thInfoCb = TestHelperInfoCB()
        cs.infocb = thInfoCb.enqueue

        self.assertEqual(1, cs.GL_INIT(18, 'N',2,14,5))
        self.assertTrue(thInfoCb.compareLastWith(101, "INFO", "1 GL 18 N 2 14 5"))
        dd = [False] * 5
        self.assertEqual(1, cs.GL_SET(18,1,12,14,dd))

    def test_Simulated_FB(self):
        cs = controlstationSimulated.controlstationSimulated()
        thInfoCb = TestHelperInfoCB()
        cs.infocb = thInfoCb.enqueue

        self.assertEqual(1, cs.FB_SET(12,True))
        self.assertTrue(thInfoCb.compareLastWith(100, "INFO", "1 FB 12 1"))
        self.assertEqual(1, cs.FB_SET(12,False))
        self.assertTrue(thInfoCb.compareLastWith(100, "INFO", "1 FB 12 0"))
        self.assertEqual(1, cs.FB_SET(12,False))
        self.assertTrue(thInfoCb.compareLastWith(100, "INFO", "1 FB 12 0"))


if __name__ == '__main__':
    unittest.main()
