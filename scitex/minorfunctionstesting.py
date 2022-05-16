import minorfunctions


class EqualTester():
    def totalEqualTest(self):
        self.equalTest()
        self.greaterEqualTest()
        self.lesserEqualTest()
        self.errorEqualTest()

    def equalTest(self):
        assert minorfunctions.areEqual(8, 8) == True

    def greaterEqualTest(self):
        assert minorfunctions.areEqual(100, 102) == False
        assert minorfunctions.areEqual(100, 102, 1) == False

    def lesserEqualTest(self):
        assert minorfunctions.areEqual(100, 98) == False
        assert minorfunctions.areEqual(100, 98, 1) == False

    def errorEqualTest(self):
        assert minorfunctions.areEqual(100, 90) == False
        assert minorfunctions.areEqual(100, 90, 10) == True
        assert minorfunctions.areEqual(100, 95, 4) == False


eq = EqualTester()
eq.totalEqualTest()
