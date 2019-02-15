import sys, glob
def getCollabs( labSec,labNo ):
    collabs = {}
    labNo = str( labNo ) if int( labNo ) >= 10 else '0' + str( labNo )
    files = glob.glob( f"/class/cs101/etc/sxns/AY{labSec}/submitted/*/lab{labNo}/netids.txt" )
    from string import whitespace as w
    from string import punctuation as p
    from string import printable
    for f in files:
        with open( f ) as openF:
            path_elems = f.split( '/' )
            submitter = path_elems[ path_elems.index( 'submitted' )+1 ]
            data = openF.read().strip()
            #print( f,'\n',submitter,':',data )
            collabs[ submitter ] = data.split()
    #print ( collabs )
    return collabs

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract collaborators from NB grader and output collab info')
    parser.add_argument('section', metavar='{A-Q}', nargs='?', help='section name (one character)')
    parser.add_argument('no' , metavar='XX', nargs='?', help='labNo')
    
    args = parser.parse_args()
    collabs = getCollabs(args.section, args.no)
    for collab in collabs:
        print( f'{collab}:  ',end='' )
        for collaborator in collabs[ collab ]:
            print( f'{collaborator},',end='' )
        print()
