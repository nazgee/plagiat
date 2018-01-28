# -*- coding: utf-8 -*-
#!/usr/local/bin/python2.7

import sys
import csv
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import traceback
import string
import tempfile
import subprocess



# M=67
# - genome-wide association study of alcohol use disorder identification test (audit) scores in 20 328 research participants of european ancestry.
# - identification of novel risk loci for restless legs syndrome in genome-wide association studies in individuals of european ancestry: a meta-analysis.

class Parser(object):
    def __init__(self, data):
        self.data = data
        self.title1 = None
        self.title2 = None
        self.metric = None
        
    def setMetric(self, metric):
        self.metric = metric
    
    def setTitle1(self, title1):
        self.title1 = title1
        
    def setTitle2(self, title2):
        self.title1 = title2
    
    def dump(self):
        print "metric=" + str(self.metric)
        print "title1=" + self.title1
        print "title2=" + self.title2
        with tempfile.NamedTemporaryFile() as temp1:
            temp1.write(self.title1)
            temp1.flush()
            with tempfile.NamedTemporaryFile() as temp2:
                temp2.write(self.title2)
                temp2.flush()

                subprocess.call(["wdiff", "-w", "\033[0;31m", "-x", "\033[0m", "-y", "\033[0;32m", "-z", "\033[0m", temp1.name, temp2.name])
                print ""
    
    def feed (self, line):
        line = line.rstrip()
        if (line.startswith("M=")):
            self.title1 = None
            self.title2 = None
            self.metric = line.strip("M=")
        elif (self.title1 == None):
            self.title1 = line.strip("- ")
        elif (self.title2 == None):
            self.title2 = line.strip("- ")
            self.dump()
        

def showme(filedata, filetitles):
    myparser = Parser(filedata)
    with open(filetitles, mode="r") as fv:
        for line in fv:
            myparser.feed(line)
        
    pass

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    try:
        # Setup argument parser
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("--verbose", dest="verbose", action='store_true', help="be verbose", default=True)
        parser.add_argument("--data", dest="filedata", nargs='?', help="file to read titles from [default: %(default)s]", default='pubmed_result.csv')
        parser.add_argument("--titles", dest="filetitles", nargs='?', help="file to read titles from [default: %(default)s]", default='titles.txt')

        # Process arguments
        args = parser.parse_args()
        
        if (args.verbose):
            print "====="
            print "data        = " + args.filedata
            print "titles      = " + args.filetitles
            print "====="

        showme(args.filedata, args.filetitles)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(main())