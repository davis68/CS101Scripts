import sys, glob
def getCollabs(labSec, labNo):
    collabs = {} # to return
    files = glob.glob("/class/cs101/etc/sxns/AY"+labSec+"/submitted/*/lab"+labNo+"/netids.txt")
    from string import whitespace as w
    from string import punctuation as p
    from string import printable
    for f in files:
        with open(f) as openF:
            submitter = path[path.index('submitted')+1]
            data = openF.read().strip()
            collabs[submitter] = data.split()
    print (collabs)
    return collabs

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract collaborators from NB grader and output collab info')
    parser.add_argument('section', metavar='{A-Q}', nargs='?', help='section name (one character)')
    parser.add_argument('no' , metavar='XX', nargs='?', help='labNo')
    
    args = parser.parse_args()
    print (getCollabs(args.section, args.no))
