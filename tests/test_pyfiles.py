#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
__version__=''' $Id: test_pyfiles.py 3660 2010-02-08 18:17:33Z damian $ '''
"""Tests performed on all Python source files of the ReportLab distribution.
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, SecureTestCase, GlobDirectoryWalker, outputfile, printLocation
setOutDir(__name__)
import os, sys, string, fnmatch, re
import unittest
from reportlab.lib.utils import open_and_read, open_and_readlines, isStrType

class AsciiFileTestCase(unittest.TestCase):
    "Test if Python files are pure ASCII ones."

    def testAscii(self):
        "Test if Python files are pure ASCII ones."
        from reportlab.lib.testutils import RL_HOME
        allPyFiles = GlobDirectoryWalker(RL_HOME, '*.py')

        for path in allPyFiles:
            fileContent = open_and_read(path,'r')
            nonAscii = u''.join(list(set([c for c in fileContent if ord(c)>127])))

            truncPath = path[path.find('reportlab'):]
            args = (truncPath, repr(map(ord, nonAscii)))
            msg = "File %s contains characters: %s." % args
            assert len(nonAscii) == 0, msg


class FilenameTestCase(unittest.TestCase):
    "Test if Python files contain trailing digits."

    def testTrailingDigits(self):
        "Test if Python files contain trailing digits."

        from reportlab.lib.testutils import RL_HOME
        allPyFiles = GlobDirectoryWalker(RL_HOME, '*.py')

        for path in allPyFiles:
            #hack - exclude barcode extensions from this test
            if path.find('barcode'):
                pass
            else:
                basename = os.path.splitext(path)[0]
                truncPath = path[path.find('reportlab'):]
                msg = "Filename %s contains trailing digits." % truncPath
                assert basename[-1] not in string.digits, msg

    ##            if basename[-1] in string.digits:
    ##                print truncPath


class FirstLineTestCase(SecureTestCase):
    "Testing if objects in the ReportLab package have docstrings."

    def findSuspiciousModules(self, folder, rootName):
        "Get all modul paths with non-Unix-like first line."

        firstLinePat = re.compile('^#!.*python.*')

        paths = []
        for file in GlobDirectoryWalker(folder, '*.py'):
            if os.path.basename(file) == '__init__.py':
                continue
            firstLine = open_and_readlines(file)[0]
            if not firstLinePat.match(firstLine):
                paths.append(file)

        return paths

    def test1(self):
        "Test if all Python files have a Unix-like first line."

        path = outputfile("test_firstline.log")
        file = open(path, 'w')
        file.write('No Unix-like first line found in the files below.\n\n')

        from reportlab.lib.testutils import RL_HOME
        paths = self.findSuspiciousModules(RL_HOME, 'reportlab')
        paths.sort()

        for p in paths:
            file.write("%s\n" % p)

        file.close()

def makeSuite():
    suite = makeSuiteForClasses(AsciiFileTestCase, FilenameTestCase)
    if sys.platform[:4] != 'java':
        loader = unittest.TestLoader()
        suite.addTest(loader.loadTestsFromTestCase(FirstLineTestCase))
    return suite

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
