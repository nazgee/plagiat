# -*- coding: utf-8 -*-
#!/usr/local/bin/python2.7

import sys
import csv
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import traceback
import itertools
from fuzzywuzzy import fuzz

# base comparison method -- any comparison method has to inherit it
class Comparison(object):
    # TODO consider storing whole row, instead of a title
    # so a link to an article can be given when displaying results
    def __init__(self, titles, lowercase):
        self.titles = 2*[None]
        if (lowercase):
            self.titles[0] = titles[0].lower()
            self.titles[1] = titles[1].lower()
        else:
            self.titles[0] = titles[0]
            self.titles[1] = titles[1]
        
        
    def setMetric(self, metric):
        self.metric = metric

    def toString(self):
        s = "M=" + str(self.metric) + "\n"
        s = s + "- " + self.titles[0] + "\n"
        s = s + "- " + self.titles[1] + "\n"
        
        return s

# comparison method #1
class ComparisonTokenSet(Comparison):
    def __init__(self, titles, lowercase):
        super(ComparisonTokenSet, self).__init__(titles, lowercase)
        super(ComparisonTokenSet, self).setMetric(fuzz.token_set_ratio(self.titles[0], self.titles[1]))

# comparison method #2
class ComparisonTokenSort(Comparison):
    def __init__(self, titles, lowercase):
        super(ComparisonTokenSort, self).__init__(titles, lowercase)
        super(ComparisonTokenSort, self).setMetric(fuzz.token_sort_ratio(self.titles[0], self.titles[1]))

# util function to get list of comparison methods - to verify cmdline validity
def getComparisonMethods():
    return map(lambda x: x.__name__, Comparison.__subclasses__())

# util function go get comparison object type based on a string passed from cmdline
def getComparisonType(method):
    return next((x for x in Comparison.__subclasses__() if x.__name__ == method), None)

def calculateCombinationsNumber(titlesNumber):
    return titlesNumber * (titlesNumber-1) / 2



# print iterations progress - https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def printProgress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


# bells and whistles; reads .csv file, creates requested comparisons, and returns list of results
def dumpstat(inputfile="pubmed_result.csv", limitinput=5, limitoutput=5, method='tokenset', lowercase=True):

    if method not in getComparisonMethods():
        raise NotImplementedError("method " + method + " is not implemented")
    
    # list of titles limited to 'limitoutput'
    titles = []
    
    # read .csv with entries 
    with open(inputfile, mode="r") as fv:
        reader = csv.DictReader(fv)
        index = 0
        
        for row in reader:
            # respect the limits
            index = index + 1
            if (index > limitinput):
                break
            
            # skip malformed rows -- not sure why we're getting them
            if (row['Title'] == 'Title'):
                continue

            titles.append(row['Title'])
    
    # list of comparisons
    # FIXME can be lower than calculated if file is a small one
    totalComparisons = calculateCombinationsNumber(limitinput)
    comparisons = []
    
    # TODO run comparisons in parallel
    index = 0
    for pair in itertools.combinations(titles, r=2):
        c = getComparisonType(method)(pair, lowercase)
        # FIXME wasting a lot of memory here makes it impossible to work on big sets.
        # Maybe append only if better than worst of top 'limitinput' best ones
        # and use a fixed-width container capped to 'limitinput' 
        comparisons.append(c)
        
        if ((index % 1000) == 0):
            printProgress(index, totalComparisons, "Working... ")
        index = index + 1
        
    printProgress(totalComparisons, totalComparisons, "Compared!")
    
    # sort the comparison results, so better ones are first
    comparisons.sort(key=lambda x: x.metric, reverse=True)
    
    # display results
    index = 0
    for c in comparisons:
        if (index > limitoutput):
                break
        print (c.toString())
        index = index + 1

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
        parser.add_argument("--lowercase", dest="lowercase", action='store_true', help="make lowercase before comparison")
        parser.add_argument("--limitinput", dest="limitinput", type=int, help="number of titles to compare", default=sys.maxint)
        parser.add_argument("--limitoutput", dest="limitoutput", type=int, help="number of comparisons to return", default=10)
        parser.add_argument("--data", dest="filedata", nargs='?', help="file to read titles from [default: %(default)s]", default='pubmed_result.csv')
        parser.add_argument("--method", dest="method", nargs='?', help="comparison method to use, one of: {" + ', '.join(getComparisonMethods()) + "} [default: %(default)s]", default=getComparisonMethods()[0])

        # Process arguments
        args = parser.parse_args()
        
        if (args.verbose):
            print "====="
            print "data        = " + args.filedata
            print "limitinput  = " + str(args.limitinput)
            print "limitoutput = " + str(args.limitoutput)
            print "method      = " + str(args.method)
            print "lowercase   = " + str(args.lowercase)
            print "====="
        
        print "max number of combinations to check: " + str(calculateCombinationsNumber(args.limitinput))
        
        dumpstat(args.filedata, args.limitinput, args.limitoutput, args.method, args.lowercase)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(main())