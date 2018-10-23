#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def readConfiguration():
    '''
    Load the config.py file stored adjacent to this script.
    '''
    import yaml
    configData = yaml.safe_load( open( './config.yml' ) )
    try:
        pass
    except:
        raise Exception( 'You don\'t seem to have a readable configuration file in this directory.' )
    return configData


def extractGrades( gradebookDB,section,labNo ):
    '''
    Open the specified grade database and return grades.

    Input:
        filename    str

    Output:
        grades      dict
    '''
    import sys

    from nbgrader.api import Gradebook
    gb = Gradebook( gradebookDB )
    #gb = Gradebook( f'sqlite:////class/cs101/etc/sxns/{section}/gradebook.db')

    grades = {}
    for s in gb.assignment_submissions( "lab" + labNo ):
        grades[ s.student_id ] = float( s.score )
    return grades


def getCollabs(labSec, labNo):
    '''
    Identify collaborating pairs of students.

    Collaborators are listed near each other at the top of the notebook in question.
    '''
    import glob
    import json
    import os
    import sys

    collabs = {}
    files = glob.glob( f'/class/cs101/etc/sxns/{labSec}/submitted/*/lab{labNo}/*.ipynb' )

    from string import whitespace as w
    from string import punctuation as p
    from string import printable

    collabsLabel = '''List _all_ collaborators' or partners' **NetIDs** below, including your own:'''

    for file in files:
        # Load IPYNB in JSON format.
        data = json.load( open( file ) )

        # Locate collaborator label.  The collaborators are listed in the next cell.
        try:
            for cell in data[ 'cells' ][ 0:12 ]:
                if collabsLabel in cell[ 'source' ][ 0 ]:
                    #print( cell[ 'source' ][ 0 ] )
                    break
        except IndexError:
            pass
                
        #print( data[ 'cells' ][ data[ 'cells' ].index( cell ) + 1 ] )
        try:
            collabCell = data[ 'cells' ][ data[ 'cells' ].index( cell ) + 1 ]
        except IndexError:
            collabCell = { 'source':[] }

        # Parse out collaborators, which may be raw names or strings.
        if len( collabCell[ 'source' ] ) < 1:
            # No collaborators have been listed.
            continue

        names = collabCell[ 'source' ][ 0 ]
        for c in w + p:
            names = names.replace( c,' ' )
        nameList = names.split()
        nameList = [ name for name in names if name != '' ]
        nameList = [ name.strip( ',' ) for name in names ]
        nameList = [ name.strip( '\'' ) for name in names ]
        nameList = [ name.strip( '"' ) for name in names ]

        collabsList = ''.join( names ).split()
        submitter = os.path.split( os.path.split( os.path.split( file )[ 0 ] )[ 0 ] )[ -1 ]
        collabs[ submitter ] = collabsList
    return collabs


def parseArguments():
    '''
    Parse arguments.
    '''
    import argparse
    import sys

    parser = argparse.ArgumentParser( description='''Extract grades from NB grader and output compass compatible csv files.\n\nUsage:\n\tpython3 ultimateGradeCal.py 3\nto read lab03.''' )
    parser.add_argument( 'lab',nargs=1,help='lab' )
    parser.add_argument( '-c','--collabs',metavar="Y/N",nargs = '?',help="Fetch collaborator information",default="Y" )
    parser.add_argument( '-o','--output',metavar='output',nargs='?',help='csv file to upload to compass',default = sys.stdout )

    return parser.parse_args()


def parseGrades( grades,scale ):
    '''
    Parse grades into proper scaling for grading (specified by scale).
    '''
    maxGrade = grades[ max( grades,key=grades.get ) ]
    if maxGrade == 0:
        # When the maximum grade is zero, it is a MATLAB lab or otherwise participation--based.
        for key, value in grades.items():
            grades[ key ] = 2.0
    else:
        # Otherwise, scale appropriately from the highest grade.
        for key,value in grades.items():
            grades[ key ] = value / maxGrade * scale
    return grades


def writeGradesOut( grades,labNo,collabs,outputFileName ):
    '''
    Write grades out to a Compass-compatible CSV file.  This can be a single
    column or the entire gradebook.  By default, Compass outputs UTF-16-encoding.
    '''
    import pandas as pd

    df = pd.read_csv( outputFileName,encoding='utf-16',delimiter=',' )
    if df.shape[ 1 ] == 1:    
        df = pd.read_csv( outputFileName,encoding='utf-16',delimiter='\t' )
    df = df.set_index( 'Username',drop=False )

    for column in df.columns:
        if 'lab '+labNo in column.lower() or 'lab'+labNo in column.lower():
            break

    for student in grades:
        try:
            df.loc[ student,column ] = grades[ student ]
            if student in collabs:
                #print( student,collabs[student] )
                for collab in collabs[ student ]:
                    if collab == '': continue
                    #print( collab,grades[ student ] )
                    df.loc[ collab,column ] = grades[ student ]
        except KeyError:
            pass

    df.to_csv( outputFileName,encoding='utf-16',index=False )


def main():
    # Read in configuration. ###################################################
    args = parseArguments()
    config = readConfiguration()

    gradebookDB    = config[ 'gradebookDB' ]
    csvFileName    = config[ 'rosterFile' ]
    labSec         = config[ 'section' ]
    labNo          = args.lab[ 0 ] if len( args.lab[ 0 ] ) == 2 else '0' + args.lab[ 0 ]
    gradeScale     = config[ 'scale' ]
    outputFileName = config[ 'outputFile' ]
    if config[ 'debug' ]: print( csvFileName,labSec,labNo,gradeScale,outputFileName )

    # Read in grades. ##########################################################
    grades = {}
    grades.update( extractGrades( gradebookDB,labSec,labNo ) )
    grades = parseGrades( grades,gradeScale )
    if config[ 'debug' ]: print( grades )

    # Identify collaborators. ##################################################
    collabs = {}
    if args.collabs.upper() == 'Y':
        collabs.update( getCollabs( labSec,labNo ) )
    if config[ 'debug' ]: print( collabs )

    # Format grades. ###########################################################
    writeGradesOut( grades,labNo,collabs,outputFileName )


if __name__ == "__main__":
    main()
