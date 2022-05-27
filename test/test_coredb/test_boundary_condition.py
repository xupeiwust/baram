import unittest

from coredb import coredb


class TestBoundaryCondition(unittest.TestCase):
    def setUp(self):
        self.db = coredb.CoreDB()

    def tearDown(self) -> None:
        del coredb.CoreDB._instance

    def testAddBoundaryCondition(self):
        name = 'testBoundaryCondition_1'
        geometricalType = 'patch'
        index = self.db.addBoundaryCondition(name, geometricalType)
        bcs = self.db.getBoundaryConditions()
        self.assertIn((index, name, 'wall'), bcs)
        self.assertEqual(1, len(bcs))

    def testAddBoundaryConditionIndex(self):
        name = 'testBoundaryCondition_1'
        physicalType = 'patch'
        self.db.addBoundaryCondition(name, physicalType)
        index = self.db.addBoundaryCondition('second', physicalType)
        self.assertEqual(2, index)


if __name__ == '__main__':
    unittest.main()
