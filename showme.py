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
import re



# M=67
# - genome-wide association study of alcohol use disorder identification test (audit) scores in 20 328 research participants of european ancestry.
# - identification of novel risk loci for restless legs syndrome in genome-wide association studies in individuals of european ancestry: a meta-analysis.

col_green = "\033[42m"
col_red = "\033[43m"
col_escape = "\033[0m"

class Parser(object):
    
    def __init__(self, data):
        self.data_file = data
        self.title1 = None
        self.title2 = None
        self.metric = None
        self.data_reader = csv.reader(open(data, "r"))
        
    def setMetric(self, metric):
        self.metric = metric
    
    def setTitle1(self, title1):
        self.title1 = title1
        
    def setTitle2(self, title2):
        self.title1 = title2
    
    def getInfo(self, title):
        self.data_reader = csv.reader(open(self.data_file, "r"))
        for row in self.data_reader:
            if (row[0].lower() == title.strip()):
                return "https://www.ncbi.nlm.nih.gov" + row[1] + " " + row[2]

        return "?"
    
    def dump(self):
        info1 = self.getInfo(self.title1)                
        info2 = self.getInfo(self.title2)

        self.title1 = self.title1.rstrip('.') + " "
        self.title2 = self.title2.rstrip('.') + " "

        with tempfile.NamedTemporaryFile() as temp1:

            
            temp1.write(self.title1)
            temp1.flush()
            with tempfile.NamedTemporaryFile() as temp2:
                temp2.write(self.title2)
                temp2.flush()



                proc = subprocess.Popen(["wdiff", "-w", "col_green", "-x", "col_escape", "-y", "col_red", "-z", "col_escape", temp1.name, temp2.name], stdout=subprocess.PIPE)
                output = proc.stdout.read()
                
                matches1 = re.findall("col_green" + "(.*?)" + "col_escape" ,output)
                matches2 = re.findall("col_red" + "(.*?)" + "col_escape" ,output)
                output = output.replace("col_green", col_green)
                output = output.replace("col_red", col_red)
                output = output.replace("col_escape", col_escape)

                
                for pat in matches1:
                    self.title1 = self.title1.replace(" " + pat + " ", " " + col_green + pat + col_escape + " ", 1)
                    
                for pat in matches2:
                    self.title2 = self.title2.replace(" " + pat + " ", " " + col_red + pat + col_escape + " ", 1)
                  
                
                print "Metryka  = " + str(self.metric)  
                print "Tytuł1   =" + self.title1
                print "Tytuł2   =" + self.title2
#                 print "Tytuł1+2 =" + output
                print "Info1    = " + info1
                print "Info2    = " + info2
                print ""
    
    def feed (self, line):
        line = line.rstrip()
        if ("M=" in line):
            self.title1 = None
            self.title2 = None
            self.metric = re.sub(".*M=", "", line)
        elif (self.title1 == None):
            self.title1 = " " + line.strip("- ")
        elif (self.title2 == None):
            self.title2 = " " + line.strip("- ")
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
        
        if (False and args.verbose):
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