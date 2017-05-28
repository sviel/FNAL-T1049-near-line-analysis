import codecs

inFileName = "./data/May20/trackHitOutfileRun323.txt"
outFileName = inFileName.rstrip(".txt") + "_sample.txt"

print "Input file:", inFileName
print "Output file:", outFileName

inFile = codecs.open( inFileName, 'r' ).read().splitlines()
outFile = open( outFileName, 'w' )

for line in inFile:
    if int( line.split('\t')[0] ) < 4096:
        outFile.write(line + '\n')

