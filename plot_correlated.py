import ROOT
import os.path
import sys
import array
import codecs

from math import *
from numpy import average
from commands import getstatusoutput as shell

import AtlasStyle
from ChannelMapping import *  # use PositionStrip( Channel, VMM )


#________________________________________________________________________________

max_print = 5

pedestal = 800
pitch = 3.2
sTGC_thickness = 51.05

## Pixel module positions
##   The coordinate system origin is the centre of Pix0
pix_zpos = { 'Pix0' : 0.,
             'Pix1' : 132.52,
             'Pix2' : 274.07,
             'Pix3' : 914.07,
             'Pix4' : 1032.46,
             'Pix5' : 1154.41,
           }

## Module minus one, front surface position
L1_xpos = -365. - 5.    # correction for pixel center wrt corner
L1_ypos = -573. - 10.   # correction for pixel center wrt corner
L1_zpos =  531.25

## Sixty by forty, front surface position +- 5 mm
SF_xpos = -300.
SF_ypos = -165.
SF_zpos = pix_zpos['Pix5'] + 695.


# Table positions, in the table coordinate system
table_pos = { 'calib' : [ 2262, 435.1 ],
                                          ## Early runs with placeholder position (not found in logbook)
              '00000' : [ 2262, 435.1 ],  # Cosmic run
              '00004' : [ 2262, 435.1 ],  
              '00006' : [ 2262, 435.1 ],  
              '00007' : [ 2262, 435.1 ],  
              '00008' : [ 2262, 435.1 ],  # L4 hole
              '00016' : [ 2262, 435.1 ],  
                                          ## These runs are with neighbours off
              '00038' : [ 2157, 464.8 ],  
              '00039' : [ 1954, 465.2 ],  
              '00040' : [ 2573, 465.  ],  
              '00044' : [ 2573, 442.  ],  # L4 channel 20 hole
              '00045' : [ 1944, 442.  ],  # L4 channel 20 hole
              '00046' : [ 2355, 441.9 ],  
                                          ## Neighbours on from this point unless indicated
              '00059' : [ 2355, 441.9 ],  # GOOD
              '00062' : [ 2574, 442.0 ],  
              '00065' : [ 2573, 415.2 ],  
              '00066' : [ 2355, 415.2 ],  
              '00067' : [ 2355, 395.2 ],  
              '00068' : [ 2575, 395.2 ],  
              '00069' : [ 1933, 395.4 ],  
              '00077' : [ 1933, 395.4 ],  
              '00081' : [ 1923, 465.4 ],  
              '00082' : [ 2355, 465.3 ],  # L4 hole, L3 bad
              '00083' : [ 2355, 469.3 ],  # L4 hole, L3 bad
              '00084' : [ 2355, 469.3 ],  # L4 hole, L3 bad
              '00088' : [ 2355, 469.3 ],  # L4 hole, L3 bad
              '00089' : [ 2243, 483.1 ],  # L4 hole, L3 bad
              '00090' : [ 2243, 424.6 ],  
              '00091' : [ 2243, 394.3 ],  # L2 hole
              '00092' : [ 2181, 394.2 ],  # L2 hole
              '00093' : [ 2180, 394.2 ],  # L2 hole
              '00094' : [ 2180, 465.2 ],  # L4 hole
              '00095' : [ 2180, 465.2 ],  
              '00096' : [ 2180, 465.2 ],  
              '00097' : [ 1922, 395.4 ],  # weird L4
              '00098' : [ 1922, 395.4 ],  
              '00099' : [ 1922, 344.1 ],  # L2 hole
              '00100' : [ 1922, 430.7 ],  # low stats
              '00101' : [ 1920, 430.2 ],  # GOOD, but check TDO in layer 2
              '00103' : [ 2303, 435.4 ],  # GOOD
              '00104' : [ 2500, 435.4 ],  # GOOD
              '00106' : [ 2500, 369.4 ],  # low stats
              '00107' : [ 2500, 369.4 ],  # L3S3 unsynched
              '00108' : [ 2500, 369.4 ],  
              '00116' : [ 2181, 394.7 ],  # L2 hole
              '00119' : [ 2181, 394.7 ],  # L2 hole, neighbours off
              '00121' : [ 2183, 394.9 ],  # L2 dead channels?
              '00123' : [ 2180, 327.6 ],  # GOOD
              '00138' : [ 2182, 405.  ],  # GOOD
              '00141' : [ 2182, 360.5 ],  # GOOD
              '00144' : [ 2181, 404.2 ],  # low stats, neighbours off
                                          ## Runs 320-335: synchronized with pixels!
              '00320' : [ 2181, 402.7 ],  # ylogbook = 404.2  # low stats, partial sTGC
              '00321' : [ 2183, 402.7 ],  # ylogbook = 404.2  # GOOD
              '00323' : [ 2183, 360.1 ],  # ylogbook = 360.6  # GOOD
              '00325' : [ 2183, 340.2 ],  # L2 hole (still get L1,L3,L4 res. from pixel track)
              '00326' : [ 2183, 328.2 ],  # GOOD
              '00334' : [ 2354, 328.2 ],  # GOOD, with 40x60
              '00335' : [ 2354, 328.2 ],  # GOOD, with 40x60
            }

pixelRunMap = { '00038' : '202',
                '00084' : '252',
                '00089' : '253',
                '00090' : '254',
                '00091' : '255',
                '00092' : '256',
                '00093' : '257',
                '00094' : '258',
                '00095' : '259',
                '00096' : '261',
                '00097' : '262',
                '00098' : '263',
                '00099' : '264',
                '00101' : '265',
                '00103' : '266',
                '00104' : '267',                
                '00106' : '268',
                '00107' : '269',
                '00108' : '270',
                '00121' : '271',
                '00123' : '272',
                '00320' : '320',  # sTGC standalone 145
                '00321' : '321',  # sTGC standalone 145
                '00323' : '323',  # sTGC standalone 146
                '00325' : '325',  # sTGC standalone 148
                '00326' : '326',  # sTGC standalone 149
                '00334' : '334',  # sTGC standalone 150
                '00335' : '335',  # sTGC standalone 151
              }

offset = { 'L1S3' :  0.,
           'L2S3' : -0.5,
           'L3S3' :  0.,
           'L4S3' : -0.5,
           'L1P'  :  0.,
           'L2P'  :  0.,
           'L3P'  :  0.,
           'L4P'  :  0.,
           'L1F'  :  0.,   # ASK MEIR
           'L2F'  : -0.5,  # ASK MEIR
         }

# sine curve for correction, format a b c d
#     where a is the amplitude
#           b is the frequency
#           c is the vertical offset
#           d is the horizontal offset
sincurve = { '1S2S' : [0.059, 1.000, -0.548, 0.],
             '1S3S' : [0.018, 1.016, -0.077, 0.],
             '1S4S' : [0.063, 1.000, -0.593, 0.],
           }


zhalfgap = 1.4
#zwire_pos = [ 0., 11.25, 22.70, 33.95 ]  ## wrt L1 wire
zwire_pos = [ 8.55, 19.80, 31.25, 42.50 ]  ## wrt sTGC surface

## Strip and pad positions
#zpos_strip_pad = { 'L1S3' : zwire_pos[0] + zhalfgap + L1_zpos,
#                   'L2S3' : zwire_pos[1] - zhalfgap + L1_zpos,
#                   'L3S3' : zwire_pos[2] + zhalfgap + L1_zpos,
#                   'L4S3' : zwire_pos[3] - zhalfgap + L1_zpos,
#                   'L1P'  : zwire_pos[0] - zhalfgap + L1_zpos,
#                   'L2P'  : zwire_pos[1] + zhalfgap + L1_zpos,
#                   'L3P'  : zwire_pos[2] - zhalfgap + L1_zpos,
#                   'L4P'  : zwire_pos[3] + zhalfgap + L1_zpos,
#                 }

## The most meaningful position for the hit is the wire position
zpos = { 'L1S3' : zwire_pos[0] + L1_zpos,
         'L2S3' : zwire_pos[1] + L1_zpos,
         'L3S3' : zwire_pos[2] + L1_zpos,
         'L4S3' : zwire_pos[3] + L1_zpos,
         'L1P'  : zwire_pos[0] + L1_zpos,
         'L2P'  : zwire_pos[1] + L1_zpos,
         'L3P'  : zwire_pos[2] + L1_zpos,
         'L4P'  : zwire_pos[3] + L1_zpos,
         'L1F'  : zwire_pos[0] + SF_zpos,  # ASK MEIR
         'L2F'  : zwire_pos[1] + SF_zpos,  # ASK MEIR
       }

BinMap = { 0 : 'L1S3',
           1 : 'L2S3',
           2 : 'L3S3',
           3 : 'L4S3',
           4 : 'L1P' ,
           5 : 'L2P' ,
           6 : 'L3P' ,
           7 : 'L4P' ,
           8 : 'L1F' ,
           9 : 'L2F' ,
         }

DblSMap = { '1S2S' : 1,
            '1S3S' : 2,
            '1S4S' : 3,
            '3S2S' : 4,
            '2S4S' : 5,
            '3S4S' : 6,
          }


#________________________________________________________________________________

def read_file_sTGC(file1, stgc_run, IPMap, bad_layers = [], fullPrint = False):
    """Reads correlated decoded human-readable sTGC data."""
    
    events = {}
        
    for line in file1:
    
        if len(line) == 0 or not line[0].isdigit():
            continue
        
        buff = line.split('\t')
        #counter = int(buff[0])
        counter = int(buff[5])    ## Trigger number
        
        address = float(buff[1])
        tdoTemp = float(buff[2])
        pdoTemp = float(buff[3]) - pedestal  ### Subtract pedestal here ###
        card_ip = int(buff[4])
        

        card_sector = IPMap[card_ip]
        
        ## correct for readout inversion
        if card_sector[1:3] in ['2S','3S']:
            address = 63 - address

        
        ## Skip bad layers
        if card_ip in bad_layers:
            continue
                        
        ## Skip bad regions
        if stgc_run in ['00059'] \
          and card_sector[1:3] == '4S' and address < 10:
            continue                

        if stgc_run in ['00093','00094'] \
          and card_sector[1:3] == '1S' and address < 10:
            continue                
        
        elif stgc_run in ['00097','00099','00100','00101','00103','00104'] \
          and card_sector[1:3] == '1S' and address < 20:
            continue              

        elif stgc_run > '00104' and stgc_run < '00320' \
          and card_sector[1:3] == '1S' and address < 25:
            continue
        
        elif stgc_run in ['00320','00321'] \
          and card_sector[1:3] == '1S' and address < 29:
            continue
        
        elif stgc_run > '00321' \
          and card_sector[1:3] in ['1S','2S'] and address < 41:
            continue


        ## Note: only correct for strip offset after fitting clusters!

        hit = [counter, address, tdoTemp, pdoTemp, card_ip]
        if fullPrint: print hit
        
        if counter not in events:
            events[counter] = {}
        if card_ip not in events[counter]:
            events[counter][card_ip] = []
        
        events[counter][card_ip].append( hit )
        
        
    ## Skip bad layers
    for bad_ip in bad_layers:
        del IPMap[bad_ip]
    
    return events
    
#________________________________________________________________________________


def read_file_Pixel(file2, pixel_run, fullPrint = False):
    """Reads decoded human-readable pixel data."""
    
    pix_events = {}
    pix_counters = []
    pix_layers = []
    skip = False
        
    for line in file2:
    
        if len(line) == 0 or not line[0].isdigit():
            continue
        
        pix_buff = line.split('\t')
        pix_counter = int(pix_buff[0]) + 1  ## Correct event number offset
        if pix_buff[1] != 'P':
            raise RuntimeError("Missing letter P")
            
        pix_channel = pix_buff[2]
        pix_y = -float(pix_buff[3])
        pix_x = -float(pix_buff[4])
        
        
        pix_hit = [pix_counter, pix_channel, pix_x, pix_y]
        if fullPrint: print pix_hit
        
        # Check if new event, if so reset
        if pix_counter not in pix_events:
            pix_events[pix_counter] = []
            pix_layers = []
            skip = False
            pix_counters.append(pix_counter)
        
        # Check if repeated pixel layer
        #   to pick only the first of multiple tracks from each event
        if pix_channel in pix_layers:
            skip = True
        else:
            pix_layers.append(pix_channel)
        
        # Append hit to event if desired
        if not skip:
            pix_events[pix_counter].append( pix_hit )
            if len(pix_events[pix_counter]) > 6:
                print pix_events[pix_counter]
                raise RuntimeError('Repeated pixel channel! Event number' + pix_counter)
        
    return pix_events, pix_counters
    
#________________________________________________________________________________


#=====================
#    MAIN PROGRAM
#=====================

ROOT.gROOT.ForceStyle()
AtlasStyle.SetAtlasStyle()

ROOT.gStyle.SetLabelSize(0.04,'x')
ROOT.gStyle.SetLabelSize(0.04,'y')
ROOT.gStyle.SetLabelSize(0.04,'z')
ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetLineWidth(2)
ROOT.TGaxis.SetMaxDigits(4)


if len(sys.argv) not in range(3,10):
    print '\nUsage:  plot_correlated.py <filename> <outdir> [doBeam doFast doWholeRun doPixel doSynch doAtone]\n'
    sys.exit(2)


#inFileName = '/Users/sviel/T1049/data/May20/vmm000323_decoded'
inFileName = sys.argv[1]
inDir = inFileName[:inFileName.rindex('/')+1]
outDir = sys.argv[2] + '/'

Date = inFileName.split('/')[-2]
stgc_run = inFileName.split('/')[-1].lstrip("FL").rstrip("_decoded")
if Date in ['May20','May20b']:
    stgc_run = inFileName.split('/')[-1].lstrip("vmm")[1:].rstrip("_decoded")


yvmm_min = table_pos[stgc_run][1] - table_pos['calib'][1] + PositionStrip( 0, 'L1S3' ) + L1_ypos
yvmm_max = yvmm_min + 64 * pitch

pix_yrange = 15.


doBeam = False
try:
    doBeam = int(sys.argv[3])
except(IndexError, ValueError):
    print "doBeam: Index or Value Error, setting to False"
    
if doBeam:
    print "Mode: BEAM"
else:
    print "Mode: COSMICS"


doFast = True
try:
    doFast = int(sys.argv[4])
except(IndexError, ValueError):
    print "doFast: IndexError, setting to True"
    
if doFast:
    print "Will NOT perform cluster fits"
else:
    print "Will perform cluster fits"


doWholeRun = True
try:
    doWholeRun = int(sys.argv[5])
except(IndexError, ValueError):
    print "doWholeRun: Index or Value Error, setting to True"

if doWholeRun:
    print "Whole RUN"
else:
    print "Small sample"


doPixel = False
try:
    doPixel = int(sys.argv[6])
except(IndexError, ValueError):
    print "doPixel: Index or Value Error, setting to False"

if doPixel:
    print "Run with PIXELS"
else:
    print "Run without pixels"


doSynch = False
try:
    doSynch = int(sys.argv[7])
except(IndexError, ValueError):
    print "doSynch: Index or Value Error, setting to False"

if doPixel:
    if doSynch:
        print "Run only on MATCHING events"
    else:
        print "No matching requirement"
elif doSynch:
    print "doSynch: Need pixels for matching, setting to False"
    doSynch = False


doAtone = False  ## Atone for our sins (that is, enable sine wave correction)
try:
    doAtone = int(sys.argv[8])
except(IndexError, ValueError):
    print "doAtone: Index or Value Error, setting to False"

if doAtone:
    print "APPLY the structure pattern corrections"
else:
    print "No structure pattern correction"


#-----------------------------
# Initialize IP map

IPMap = {}
bad_layers = []

if Date in ['May13', 'May14']:    # Initial setup
    IPMap = { 24 : 'L1S3',
              19 : 'L2S3',
              25 : 'L3S3',
              18 : 'L4S3',
              26 : 'L1P' ,
              16 : 'L2P' ,
              23 : 'L3P' ,
              22 : 'L4P' ,
            }

elif Date in ['May15','May15_pulse','May16']:    # Starting May 14, 20h50
#    bad_layers = [18]
    IPMap = { 21 : 'L1S3',
              19 : 'L2S3',
              25 : 'L3S3',
              18 : 'L4S3',
              26 : 'L1P' ,
              16 : 'L2P' ,
              23 : 'L3P' ,
              22 : 'L4P' ,
            }

elif Date in ['May16b']:    # Starting May 16, 19h50
    IPMap = { 21 : 'L1S3',
              19 : 'L2S3',
              25 : 'L3S3',
              18 : 'L4S3',
            }

elif Date in ['May17']:    # Starting May 17, 10h52
    IPMap = { 25 : 'L1S3',
              18 : 'L2S3',
              22 : 'L3S3',
              19 : 'L4S3',
            }

elif Date in ['May18b']:    # Starting May 18, 16h15
    bad_layers = [24]
    IPMap = { 25 : 'L1S3',
              18 : 'L2S3',
              24 : 'L3S3',
              19 : 'L4S3',
              17 : 'L1P',
              20 : 'L2P',
            }

elif Date in ['May18','May19','May20','May20b']:    # Starting May 18, 21h45
    if Date in ['May20b']:
        bad_layers = [18]
    IPMap = { 25 : 'L1S3',
              18 : 'L2S3',
              29 : 'L3S3',
              19 : 'L4S3',
              17 : 'L1P',
              20 : 'L2P',
            }

elif Date in ['May20c']:    # Starting May 20, 18h30
    IPMap = { 25 : 'L1S3',
              18 : 'L2S3',
              29 : 'L3S3',
              19 : 'L4S3',
              20 : 'L2P',
              22 : 'L1F',
              17 : 'L2F',
            }

else:
    raise RuntimeError( "Error reading IP map: Invalid date" )
    

#-----------------------------
# Read input files

if doWholeRun:
    inFileName += ".txt"
else:
    inFileName += "_sample.txt"

print "Input sTGC file:", inFileName
inFile = codecs.open( inFileName, 'r' ).read().splitlines()
Events = read_file_sTGC( inFile, stgc_run, IPMap, bad_layers, fullPrint = False )

pixel_run = None
PixelEvents = None
pix_counters = []
if doPixel:
    pixel_run = pixelRunMap[stgc_run]
    try:
        if doWholeRun:
            inFilePixelName = inDir + "trackHitOutfileRun" + pixel_run + ".txt"
        else:
            inFilePixelName = inDir + "trackHitOutfileRun" + pixel_run + "_sample.txt"
        print "Pixel run file:", inFilePixelName
        inFilePixel = codecs.open( inFilePixelName, 'r' ).read().splitlines()
        PixelEvents, pix_counters = read_file_Pixel( inFilePixel, pixel_run, fullPrint = False )
    except IOError:
        print "Pixel run file not found!  Setting doPixel = False"
        doPixel = False
    

#for ievent, event in Events.iteritems():
#    if ievent > 100: break
#    if len(event) < 2: continue
#    for ip, vmm in event.iteritems():
#        print vmm
#sys.exit(0)


#-----------------------------
# Prepare output directory for plots

if doWholeRun:
    outDir += 'plots/'
else:
    outDir += 'plots_sample/'

if not(os.path.isdir(outDir)):
    shell('mkdir -p ' + outDir)
if not(doFast) and not(os.path.isdir(outDir + 'single_events/')):
    shell('mkdir -p ' + outDir + 'single_events/')

print "Output directory:", outDir
print


#-----------------------------
# Prepare canvas

square_Canvas = ROOT.TCanvas('square_Canvas','square_Canvas',10,10,800,800)
tracks_Canvas = ROOT.TCanvas('tracks_Canvas','tracks_Canvas',10,10,800,800)
pix_tracks_Canvas = ROOT.TCanvas('pix_tracks_Canvas','pix_tracks_Canvas',10,10,800,800)
comb_tracks_Canvas = ROOT.TCanvas('comb_tracks_Canvas','comb_tracks_Canvas',10,10,800,800)

Canvas = {}

Canvas['P'] = ROOT.TCanvas('Canvas_P','Canvas_P',10,10,3200,2400)
Canvas['S'] = ROOT.TCanvas('Canvas_S','Canvas_S',10,10,3200,2400)
Canvas['F'] = ROOT.TCanvas('Canvas_F','Canvas_F',10,10, 800,1200)
Canvas['E'] = ROOT.TCanvas('Canvas_E','Canvas_E',10,10,3200,2400)
Canvas['T'] = ROOT.TCanvas('Canvas_T','Canvas_T',10,10,3200,3200)
Canvas['Y'] = ROOT.TCanvas('Canvas_Y','Canvas_Y',10,10,2400,1600)

Canvas['P'].Divide( 2, 2 )
Canvas['S'].Divide( 2, 2 )
Canvas['F'].Divide( 1, 2 )
Canvas['E'].Divide( 2, 2 )
Canvas['T'].Divide( 2, 2 )
Canvas['Y'].Divide( 3, 2 )


#-----------------------------
# Prepare the combined track display

comb_dummy_z = []
comb_dummy_y = []

for pix_channel, pix_z in pix_zpos.iteritems():
    comb_dummy_z.append(pix_z)
    comb_dummy_y.append(- pix_yrange)
    #comb_dummy_y.append(yvmm_min)
    comb_dummy_z.append(pix_z)
    comb_dummy_y.append(pix_yrange)
    #comb_dummy_y.append(yvmm_max)

comb_dummy_arr_z = array.array('d', comb_dummy_z)
comb_dummy_arr_y = array.array('d', comb_dummy_y)
comb_dummy = ROOT.TGraph( len(comb_dummy_arr_z), comb_dummy_arr_z, comb_dummy_arr_y )
comb_dummy.GetXaxis().SetTitle("z [mm]")
comb_dummy.GetYaxis().SetTitle("y [mm]")   ## "y [pitch * strip channel]"
comb_dummy.GetYaxis().SetRangeUser(yvmm_min, yvmm_max)
comb_dummy.SetMarkerColor(10)

comb_tracks_Canvas.cd()
comb_dummy.Draw('AP')
comb_tracks_Canvas.RedrawAxis()
#comb_tracks_Canvas.Print('comb_dummy.png')


#-----------------------------
# Declare histograms

profile = {}
w_profile = {}
TDO = {}
PDO = {}

ydiag = {}
ysin = {}
ysin_fit = {}
ysin_func = {}
ysin_corrected = {}
yrot = {}
yrot_fit = {}
yrot_func = {}

ydiag_sil = {}
ysin_sil = {}
ysin_sil_fit = {}
ysin_sil_func = {}
ysin_sil_corrected = {}
yrot_sil = {}
yrot_sil_fit = {}
yrot_sil_func = {}

for ip, sector in IPMap.iteritems():
    profile[ip] = ROOT.TH1F('profile_'+sector, 'profile_'+sector, 64, 0, 64)
    w_profile[ip] = ROOT.TH1F('w_profile_'+sector, 'w_profile_'+sector, 64, 0, 64)
    TDO[ip] = ROOT.TH1F('TDO_'+sector, 'TDO_'+sector, 70, 0, 7000)
    PDO[ip] = ROOT.TH1F('PDO_'+sector, 'PDO_'+sector, 70, 0, 7000)
    ydiag_sil[sector] = ROOT.TGraph()
    ysin_sil[sector] = ROOT.TGraph()
    yrot_sil[sector] = ROOT.TH1F('yrot_sil_' + sector, 'yrot_sil_' + sector, 100, -1, 1)
    

sector_corr = ROOT.TH2F('sector_corr', 'sector_corr', 10, 0, 10, 10, 0, 10)
sector_corr_div = ROOT.TH2F('sector_corr_div', 'sector_corr_div', 10, 0, 10, 10, 0, 10)
sector_corr_sel = ROOT.TH2F('sector_corr_sel', 'sector_corr_sel', 10, 0, 10, 10, 0, 10)

for ibin, sector in BinMap.iteritems():
    sector_corr.GetXaxis().SetBinLabel( ibin+1, sector )
    sector_corr.GetYaxis().SetBinLabel( ibin+1, sector )
    sector_corr_div.GetXaxis().SetBinLabel( ibin+1, sector )
    sector_corr_div.GetYaxis().SetBinLabel( ibin+1, sector )
    sector_corr_sel.GetXaxis().SetBinLabel( ibin+1, sector )
    sector_corr_sel.GetYaxis().SetBinLabel( ibin+1, sector )

iy = -1

for DblS, iDblS in DblSMap.iteritems():
    ydiag[DblS] = ROOT.TGraph()
    ysin[DblS] = ROOT.TGraph()
    yrot[DblS] = ROOT.TH1F('yrot_' + DblS, 'yrot_' + DblS, 100, -1, 1)


#-----------------------------
# Fill histograms

for ievent, event in Events.iteritems():
    sector_is_hit = []
    
    for ip, vmm in event.iteritems():
        for hit in vmm:
            counter, address, tdoTemp, pdoTemp, card_ip = hit[0], hit[1], hit[2], hit[3], hit[4]
            
            if card_ip != ip:
                raise RuntimeError
            card_sector = IPMap[card_ip]
            
            profile[card_ip].Fill( address )
            w_profile[card_ip].Fill( address, pdoTemp )
            TDO[card_ip].Fill( tdoTemp )
            PDO[card_ip].Fill( pdoTemp )
        

        sector = IPMap[ip]
        if sector not in sector_is_hit:
            sector_is_hit.append(sector)
    
    for ibinx, sectorx in BinMap.iteritems():
        for ibiny, sectory in BinMap.iteritems():
            if (sectorx in sector_is_hit) and (sectory in sector_is_hit):
                sector_corr.Fill( ibinx, ibiny )


#-----------------------------
# Plot the sector correlations

square_Canvas.cd()

ROOT.gStyle.SetPaintTextFormat('.3f');

sector_corr.Scale( 1. / len(Events) )

sector_corr.GetXaxis().SetTitle( "2D: Coincidence rates for clusters and pads" )
sector_corr.GetZaxis().SetTitle( "Events" )
sector_corr.SetMinimum( 0. )
sector_corr.Draw('COLZTEXT')
square_Canvas.Print( outDir + 'sector_corr.png' )

for ibinx, sectorx in BinMap.iteritems():
    for ibiny, sectory in BinMap.iteritems():
        norm = sector_corr.GetBinContent(ibinx, ibinx)
        if norm != 0:
            sector_corr_div.Fill( ibinx-1, ibiny-1, sector_corr.GetBinContent(ibinx, ibiny) / norm )

sector_corr_div.GetXaxis().SetTitle( "with respect to..." )
sector_corr_div.GetYaxis().SetTitle( "Efficiency of..." )
sector_corr_div.GetZaxis().SetTitle( "Events" )
sector_corr_div.SetMinimum( 0. )
sector_corr_div.Draw('COLZTEXT')
square_Canvas.Print( outDir + 'sector_corr_div.png' )


#-----------------------------
# Plot hit profiles

print
print "Fitting hit profiles"

ROOT.gStyle.SetOptStat('eou')
ROOT.gStyle.SetOptFit(0)
Canvas['P'].Clear('D')

ROOT.gStyle.SetOptStat('e')
ROOT.gStyle.SetOptFit(111)
Canvas['S'].Clear('D')

for ip, sector in IPMap.iteritems():
    ps = sector[2]
    ipad = int(sector[1])    
    Canvas[ps].cd( ipad )
    print sector
        
    profile[ip].SetMaximum( profile[ip].GetMaximum() * 1.5 )
    if sector[1:3] in ['2S','3S']:
        profile[ip].GetXaxis().SetTitle( "63 - " + sector + " channels" )
    else:
        profile[ip].GetXaxis().SetTitle( sector + " channels" )
    profile[ip].GetYaxis().SetTitle( "Hits" )
    profile[ip].Draw('hist')
    
    if (ps == 'S') and doBeam:        
        profile_fit = profile[ip].Fit('gaus','S')
        mygauss = profile[ip].GetFunction('gaus')
        mygauss.SetLineColor(2)
        mygauss.Draw('same')        
        #print sector, ':', profile_fit.Parameter(1), profile_fit.Parameter(2)

Canvas['P'].Print( outDir + 'profile_P.png' )
Canvas['S'].Print( outDir + 'profile_S.png' )


#-----------------------------
# Plot weighted hit profiles
    
ROOT.gStyle.SetOptStat('eou')
ROOT.gStyle.SetOptFit(0)
Canvas['P'].Clear('D')

ROOT.gStyle.SetOptStat('e')
ROOT.gStyle.SetOptFit(111)
Canvas['S'].Clear('D')

for ip, sector in IPMap.iteritems():
    ps = sector[2]
    ipad = int(sector[1])    
    Canvas[ps].cd( ipad )
    print sector
            
    w_profile[ip].SetMaximum( w_profile[ip].GetMaximum() * 1.5 )
    if sector[1:3] in ['2S','3S']:
        w_profile[ip].GetXaxis().SetTitle( "63 - " + sector + " channels" )
    else:
        w_profile[ip].GetXaxis().SetTitle( sector + " channels" )
    w_profile[ip].GetYaxis().SetTitle( "ADC-weighted Hits" )
    w_profile[ip].Draw('hist')
    
    if (ps == 'S') and doBeam:        
        w_profile_fit = w_profile[ip].Fit('gaus','S')
        w_mygauss = w_profile[ip].GetFunction('gaus')
        w_mygauss.SetLineColor(2)
        w_mygauss.Draw('same')
            
Canvas['P'].Print( outDir + 'w_profile_P.png' )
Canvas['S'].Print( outDir + 'w_profile_S.png' )
    
    
#-----------------------------
# Plot TDO
    
ROOT.gStyle.SetOptStat('eou')
ROOT.gStyle.SetOptFit(0)

Canvas['P'].Clear('D')
Canvas['S'].Clear('D')

for ip, sector in IPMap.iteritems():
    ps = sector[2]
    ipad = int(sector[1])    
    Canvas[ps].cd( ipad )
    
    TDO[ip].SetMaximum( TDO[ip].GetMaximum() * 1.5 )
    TDO[ip].GetXaxis().SetTitle( sector + " TDO" )
    TDO[ip].GetYaxis().SetTitle( "Hits" )
    TDO[ip].Draw('hist')
                
Canvas['P'].Print( outDir + 'TDO_P.png' )
Canvas['S'].Print( outDir + 'TDO_S.png' )
    

#-----------------------------
# Plot PDO
    
ROOT.gStyle.SetOptStat('eou')
ROOT.gStyle.SetOptFit(0)
    
Canvas['P'].Clear('D')
Canvas['S'].Clear('D')

for ip, sector in IPMap.iteritems():
    ps = sector[2]
    ipad = int(sector[1])    
    Canvas[ps].cd( ipad )
    
    PDO[ip].SetMaximum( PDO[ip].GetMaximum() * 1.5 )
    PDO[ip].GetXaxis().SetTitle( sector + " PDO" )
    PDO[ip].GetYaxis().SetTitle( "Hits" )
    PDO[ip].Draw('hist')
                
Canvas['P'].Print( outDir + 'PDO_P.png' )
Canvas['S'].Print( outDir + 'PDO_S.png' )
    

#=============================
# PIXELS
#=============================

pix_tracks = {}
pix_tracks_func = {}
pix_angles = ROOT.TH1F('pix_angles', 'pix_angles', 100, -5, 5)

ROOT.gStyle.SetOptStat('e')
ROOT.gStyle.SetOptFit(0)
Canvas['T'].Clear('D')

if doPixel:

    #-----------------------------
    # Prepare the pixel track display
    
    pix_dummy_z = []
    pix_dummy_y = []
    
    for pix_channel, pix_z in pix_zpos.iteritems():
        pix_dummy_z.append(pix_z)
        pix_dummy_y.append(- pix_yrange)
        pix_dummy_z.append(pix_z)
        pix_dummy_y.append(pix_yrange)

    pix_dummy_arr_z = array.array('d', pix_dummy_z)
    pix_dummy_arr_y = array.array('d', pix_dummy_y)
    pix_dummy = ROOT.TGraph( len(pix_dummy_arr_z), pix_dummy_arr_z, pix_dummy_arr_y )
    pix_dummy.GetXaxis().SetTitle("z [mm]")
    pix_dummy.GetYaxis().SetTitle("y [mm]")   ## "y [pitch * strip channel]"
    pix_dummy.GetYaxis().SetRangeUser(-pix_yrange, pix_yrange)
    pix_dummy.SetMarkerColor(10)

    pix_tracks_Canvas.cd()
    pix_dummy.Draw('AP')
    pix_tracks_Canvas.RedrawAxis()
    #pix_tracks_Canvas.Print('pix_dummy.png')
    
    
    #-----------------------------
    # Loop over single pixel events
    
    for pix_ievent, pix_event in PixelEvents.iteritems():
        
        pix_track_x = []
        pix_track_y = []
        pix_track_z = []
        
        for pix_hit in pix_event:    
            pix_counter, pix_channel, pix_x, pix_y = pix_hit[0], pix_hit[1], pix_hit[2], pix_hit[3]
            
            pix_track_x.append(pix_x)
            pix_track_y.append(pix_y)
            pix_track_z.append(pix_zpos['Pix' + pix_channel])
            
                    
        pix_track_arr_x = array.array('d', pix_track_x)
        pix_track_arr_y = array.array('d', pix_track_y)
        pix_track_arr_z = array.array('d', pix_track_z)
        
        # Recover track by fitting a line
        pix_tracks[pix_ievent] = ROOT.TGraph(len(pix_track_arr_z), pix_track_arr_z, pix_track_arr_y)
        pix_track_par = pix_tracks[pix_ievent].Fit('pol1', 'SQ0')
        pix_tracks_func[pix_ievent] = pix_tracks[pix_ievent].GetFunction('pol1')
        
        pix_y_origin = pix_tracks_func[pix_ievent].GetParameter(0)
        pix_y_origin_err = pix_tracks_func[pix_ievent].GetParError(0)
        pix_slope = pix_tracks_func[pix_ievent].GetParameter(1)
        pix_slope_err = pix_tracks_func[pix_ievent].GetParError(1)
        pix_angle = atan(pix_slope)
        pix_angles.Fill( pix_angle * 1000. )  # pixel track angle in mrad
        
        pix_chi2 = pix_tracks_func[pix_ievent].GetChisquare()
        pix_ndf = pix_tracks_func[pix_ievent].GetNDF()
        
        #draw_pix_track = (pix_chi2 / pix_ndf < 10.)
        #draw_pix_track = abs(pix_angle) < 0.05
        draw_pix_track = True
        
        if not draw_pix_track:
            continue
            
    
        #-----------------------------
        # Draw the pixel tracks
        
        colour = pix_ievent % 50 + 51
        
        pix_tracks[pix_ievent].SetMarkerColor(colour)
        pix_tracks_func[pix_ievent].SetLineColor(colour)    
        
        pix_tracks_Canvas.cd()
        pix_tracks[pix_ievent].Draw('Psame')
        pix_tracks_func[pix_ievent].Draw('Lsame')
        
        comb_tracks_Canvas.cd()
        pix_tracks[pix_ievent].Draw('Psame')
        pix_tracks_func[pix_ievent].Draw('Lsame')
        
    
    #-----------------------------
    # Plot the pixel tracks
    
    pix_tracks_Canvas.Print( outDir + 'pix_tracks.png' )
    #comb_tracks_Canvas.Print( outDir + 'comb_tracks.png' )
    
    
    #-----------------------------
    # Plot the pixel track angles
    
    square_Canvas.cd()
    
    #ROOT.gStyle.SetOptStat('emrou')  ## 'eMRou'
    #ROOT.gStyle.SetOptFit(111)
    ROOT.gStyle.SetOptStat('e')
    ROOT.gStyle.SetOptFit(111)
    square_Canvas.Clear('D')
    
    pix_angles.SetMaximum( pix_angles.GetMaximum() * 1.5 )
    pix_angles.GetXaxis().SetTitle( "Track angle [mrad]" )
    pix_angles.GetYaxis().SetTitle( "Events" )
    pix_angles.Draw('hist')
    
    if pix_angles.GetEntries() != 0:
        pix_angles_fit = pix_angles.Fit('gaus','S')
        pix_angles_mygauss = pix_angles.GetFunction('gaus')
        pix_angles_mygauss.SetLineColor(2)    
        pix_angles_mygauss.Draw('same')
        
    square_Canvas.Print( outDir + 'pix_angles.png' )
    
    

#=============================
# BACK TO sTGC
#=============================

if doFast:
    sys.exit(0)   # SKIP the Gaussian fitting of clusters, etc

#-----------------------------
# Prepare the sTGC track display

dummy_z = []
dummy_y = []

for sector, z in zpos.iteritems():
    if sector[2] == 'P':
        continue
    if sector[2] == 'F' and Date != 'May20c':
        continue
    dummy_z.append(z)
    dummy_y.append(yvmm_min)
    dummy_z.append(z)
    dummy_y.append(yvmm_max)

dummy_arr_z = array.array('d', dummy_z)
dummy_arr_y = array.array('d', dummy_y)
dummy = ROOT.TGraph( len(dummy_arr_z), dummy_arr_z, dummy_arr_y )
dummy.GetXaxis().SetTitle("z [mm]")
dummy.GetYaxis().SetTitle("y [mm]")   ## "y [pitch * strip channel]"
dummy.GetYaxis().SetRangeUser(yvmm_min, yvmm_max)
dummy.SetMarkerColor(10)

tracks_Canvas.cd()
dummy.Draw('AP')
tracks_Canvas.RedrawAxis()

for ip, sector in IPMap.iteritems():
    if sector[2] != 'S':
        continue
    ipad = int(sector[1])    
    Canvas['T'].cd( ipad )
    dummy.Draw('AP')
    ROOT.gPad.RedrawAxis()


#-----------------------------
# Loop over single events

sigma_max = 5.
printed = 0
    
cutflow = {}
icut = 0

draw_me = {}
e_mygauss = {}
event_hist = {}
event_hist_means = {}
synch_diagnostic = {}

tracks = {}
tracks_unb = {}
residuals = {}
residuals_func = {}
residuals_b = {}
residuals_b_func = {}
residuals_p = {}
residuals_p_func = {}
res_mygauss = {}

angles = ROOT.TH1F('angles', 'angles', 100, -50, 50)

for ip, sector in IPMap.iteritems():
    cutflow[ip] = ROOT.TH1F('cutflow_'+sector, 'cutflow_'+sector, 10, 0, 10)

    draw_me[ip] = False
    e_mygauss[ip] = ROOT.TF1('e_mygauss_'+sector, 'gaus', 0, 64)
    e_mygauss[ip].SetLineColor(2)
    event_hist[ip] = ROOT.TH1F('event_sector_'+sector, 'event_sector_'+sector, 64, 0, 64)
    event_hist_means[ip] = ROOT.TH1F('event_means_sector_'+sector, 'event_means_sector_'+sector, 640, 0, 64)
    synch_diagnostic[ip] = ROOT.TH2F('synch_diagnostic_'+sector, 'synch_diagnostic_'+sector, 21, -10, 11, 30, -15, 15)

    if sector[2] != 'S':
        continue
    tracks_unb[sector] = []
    residuals[sector] = ROOT.TH1F('residuals_'+sector, 'residuals_'+sector, 100, -1, 1)
    residuals_b[sector] = ROOT.TH1F('residuals_b_'+sector, 'residuals_incl_'+sector, 100, -1, 1)
    residuals_p[sector] = ROOT.TH1F('residuals_p_'+sector, 'residuals_wrt_pixel_'+sector, 20, -1, 1)
    res_mygauss[sector] = ROOT.TF1('res_mygauss_'+sector, 'gaus')
    res_mygauss[sector].SetLineColor(2)


ROOT.gStyle.SetOptStat('e')
ROOT.gStyle.SetOptFit(0)
Canvas['T'].Clear()


print
print "Looping over events"
print "  Number of events:", len(Events)

for ievent, event in Events.iteritems():
    if ievent % 1000 == 0:
        print "  Event number", ievent
    
    if doSynch:
        if ievent not in pix_counters:
            continue
    
    #-----------------------------
    # Event selection
    
    strip_sectors = []
    vmm_len = []
    veto = False

    for ip, vmm in event.iteritems():
        cutflow[ip].Fill(0)
        
        sector = IPMap[ip]
        if sector[2] == 'S':
            if sector not in strip_sectors:
                strip_sectors.append(sector)
        else:
            continue   # no event selection from pads
        
        #--- Read this event ---#
        mypdo = {}
        for hit in vmm:
            counter, address, tdoTemp, pdoTemp, card_ip = hit[0], hit[1], hit[2], hit[3], hit[4]            
            mypdo[address] = pdoTemp
            
            #--- Cut: time window ---#
            if tdoTemp < 2300 or tdoTemp > 3300:
                veto = True
                
        if not veto:
            cutflow[ip].Fill(1)
            
        #--- Cut: channels per strip vmm ---#
        vmm_len.append( len(vmm) )

        if len(vmm) < 3 or len(vmm) > 5:
            veto = True
        
        if not veto:
            cutflow[ip].Fill(2)
                    
        #--- Cut: max bin not next to zero bin ---#
        max_bin = max(mypdo.iteritems(), key = lambda x:x[1])[0]
        try:
            if mypdo[max_bin - 1] <= 0 or mypdo[max_bin + 1] <= 0:
                veto = True
        except KeyError:
                veto = True

        if not veto:
            cutflow[ip].Fill(3)
            
        #--- Cut: all bins close to max ---#
        for address, pdo in mypdo.iteritems():
            if abs(address - max_bin) > 2:
                veto = True
            
        if not veto:
            cutflow[ip].Fill(4)
    
    #--- Cut: min number of strip sectors in event ---#
    if len(strip_sectors) < 4 - len(bad_layers):
        veto = True
    elif not veto:
        for ip, vmm in event.iteritems():
            cutflow[ip].Fill(5)
            
    #--- Cut: not too many clusters with only three channels ---#
    #if all(x == 3 for x in vmm_len):
    if vmm_len.count(3) > 2:          # higher is looser
        veto = True
    elif not veto:
        for ip, vmm in event.iteritems():
            cutflow[ip].Fill(6)
    
    #--- Reject event if any cut is failed ---#
    #if ievent < 20:
    #    print strip_sectors

    if veto:
        continue
        
    
    #-----------------------------
    # Event passed selection, produce histogram
    
    sector_is_hit = []
    cm_1S = None
    cluster_hits = []
    cluster_weights = []
    ypos = {}
    y_wa = {}
    
                   # This makes sure to process in order L1, L2, L3, L4
                   #   x is (ip, vmm) so IPMap[x[0]] is the sector , x[1][0] is the first hit and x[1][0][4] is the card_ip
    for ip, vmm in sorted(event.iteritems(), key = lambda x:IPMap[x[0]]):
        sector = IPMap[ip]
        if sector[2] != 'S':
            continue
        
        for hit in vmm:
            counter, address, tdoTemp, pdoTemp, card_ip = hit[0], hit[1], hit[2], hit[3], hit[4]
            
            if IPMap[card_ip] != sector:
                raise RuntimeError
            
            cluster_hits.append( address )
            cluster_weights.append( pdoTemp )
            event_hist[card_ip].Fill( address, pdoTemp )

    
        #-----------------------------
        # Draw the plots for this event hist
        
        event_hist[ip].SetMaximum( event_hist[ip].GetMaximum() * 1.5 )
        if sector[1:3] in ['2S','3S']:
            event_hist[ip].GetXaxis().SetTitle( "Event " + str(counter) + ", 63 - " + sector + " channels" )
        else:
            event_hist[ip].GetXaxis().SetTitle( "Event " + str(counter) + ", " + sector + " channels" )        
        event_hist[ip].GetYaxis().SetTitle( "ADC counts" )

        if event_hist[ip].GetEntries() != 0:
            draw_me[ip] = True
            
            ### CLUSTERS ARE FIT HERE
            
            ## Fit from histogram max bin
            max_bin = event_hist[ip].GetMaximumBin()
            event_hist_fit = event_hist[ip].Fit('e_mygauss_'+sector, 'SQ0', '', max_bin - 4, max_bin + 4)
            cluster_mean = event_hist_fit.Parameter(1)
            
            ## Weighted average
            cluster_wa = average( cluster_hits, weights = cluster_weights )
            
            
            ### Correct for strip offset HERE
            cluster_mean_corrected = None
            if doAtone:
                 ## Sine wave correction
                 sw_label = '1S'+sector[1:3]
                 if sw_label == '1S1S':
                     cm_1S = cluster_mean
                     cluster_mean_corrected = cluster_mean
                 else:
                     cluster_mean_corrected = cluster_mean + sincurve[sw_label][2] \
                         + sincurve[sw_label][0]*sin(6.2831858*(sincurve[sw_label][1]*cm_1S - sincurve[sw_label][3]))
            else:
                 ## Simple correction
                 cluster_mean_corrected = cluster_mean + offset[sector]
                 
                 
            if sector not in sector_is_hit:
                sector_is_hit.append(sector)
            ypos[sector] = cluster_mean_corrected * pitch + yvmm_min
            #y_wa[sector] = cluster_wa                ## No pitch: Vladimir wants raw weighted average
            y_wa[sector] = cluster_mean              ## Test with un-corrected Gaussian means
            if doAtone:
                y_wa[sector] = cluster_mean_corrected
            #print "    sector", sector, "mean = ", cluster_mean
            event_hist_means[ip].Fill( cluster_mean_corrected )
            

        ipad = int(sector[1])
        Canvas['E'].cd( ipad )        
        event_hist[ip].Draw('hist')
        #print "Drawing IP", ip, "=", sector, "on pad", ipad
        if draw_me[ip]:
            e_mygauss[ip].Draw('same')
            draw_me[ip] = False
    
    title = "event_" + str(ievent)
    if printed < max_print:
        Canvas['E'].Print( outDir + 'single_events/' + title + '.png' )
        printed += 1

        
    #-----------------------------
    # Now reset histograms
    
    for ip, sector in IPMap.iteritems():      
        Canvas['E'].Clear('D')
        event_hist[ip].Reset('MICES')
        event_hist[ip].SetTitle( title + "_" + sector )
    
    
    #-----------------------------
    # Fill sector correlations
    
    for ibinx, sectorx in BinMap.iteritems():
        for ibiny, sectory in BinMap.iteritems():
            if (sectorx in sector_is_hit) and (sectory in sector_is_hit):
                sector_corr_sel.Fill( ibinx, ibiny )


    #-----------------------------
    # Fill ypos correlations
    
    iy += 1
    
    try:
        ydiag['1S2S'].SetPoint( iy, y_wa['L1S3'], y_wa['L2S3'] )
        ysin['1S2S'].SetPoint( iy, y_wa['L1S3'], y_wa['L1S3'] - y_wa['L2S3'] )
        yrot['1S2S'].Fill( y_wa['L1S3'] - y_wa['L2S3'] )
    except KeyError:
        pass

    try:
        ydiag['1S3S'].SetPoint( iy, y_wa['L1S3'], y_wa['L3S3'] )
        ysin['1S3S'].SetPoint( iy, y_wa['L1S3'], y_wa['L1S3'] - y_wa['L3S3'] )
        yrot['1S3S'].Fill( y_wa['L1S3'] - y_wa['L3S3'] )
    except KeyError:
        pass

    try:
        ydiag['1S4S'].SetPoint( iy, y_wa['L1S3'], y_wa['L4S3'] )
        ysin['1S4S'].SetPoint( iy, y_wa['L1S3'], y_wa['L1S3'] - y_wa['L4S3'] )
        yrot['1S4S'].Fill( y_wa['L1S3'] - y_wa['L4S3'] )
    except KeyError:
        pass

    try:
        ydiag['3S2S'].SetPoint( iy, y_wa['L3S3'], y_wa['L2S3'] )
        ysin['3S2S'].SetPoint( iy, y_wa['L3S3'], y_wa['L3S3'] - y_wa['L2S3'] )
        yrot['3S2S'].Fill( y_wa['L3S3'] - y_wa['L2S3'] )
    except KeyError:
        pass

    try:
        ydiag['2S4S'].SetPoint( iy, y_wa['L2S3'], y_wa['L4S3'] )
        ysin['2S4S'].SetPoint( iy, y_wa['L2S3'], y_wa['L2S3'] - y_wa['L4S3'] )
        yrot['2S4S'].Fill( y_wa['L2S3'] - y_wa['L4S3'] )
    except KeyError:
        pass

    try:
        ydiag['3S4S'].SetPoint( iy, y_wa['L3S3'], y_wa['L4S3'] )
        ysin['3S4S'].SetPoint( iy, y_wa['L3S3'], y_wa['L3S3'] - y_wa['L4S3'] )
        yrot['3S4S'].Fill( y_wa['L3S3'] - y_wa['L4S3'] )
    except KeyError:
        pass
    
    for ip, sector in IPMap.iteritems():
        try:
            pix_ypos = pix_tracks_func[ievent].Eval(zpos[sector])
            ydiag_sil[sector].SetPoint( iy, ypos[sector], pix_ypos )
            ysin_sil[sector].SetPoint( iy, ypos[sector], ypos[sector] - pix_ypos )
            yrot_sil[sector].Fill( ypos[sector] - pix_ypos )
        except KeyError:
            pass
    
    
    #-----------------------------
    # Fit the track
    
    if strip_sectors > 2:
        track_z = []
        track_y = []
        track_unb_pos = {}
        for ip, sector in IPMap.iteritems():
            if sector[2] != 'S':
                continue
            track_unb_pos[sector] = []
        
        for sector, y in ypos.iteritems():
            track_z.append(zpos[sector])
            track_y.append(y)
            
            for ip, this_sector in IPMap.iteritems():
                if this_sector[2] != 'S':
                    continue
                if this_sector != sector:
                    track_unb_pos[this_sector].append( (zpos[sector], y) )
            
        track_arr_z = array.array('d', track_z)
        track_arr_y = array.array('d', track_y)
            
        tracks[ievent] = ROOT.TGraph(len(track_arr_z), track_arr_z, track_arr_y)
        track_par = tracks[ievent].Fit('pol1', 'SQ0')
        track = tracks[ievent].GetFunction('pol1')

        y_origin = track.GetParameter(0)
        y_origin_err = track.GetParError(0)
        slope = track.GetParameter(1)
        slope_err = track.GetParError(1)
        angle = atan(slope)
        angles.Fill( angle * 1000. )
        
        chi2 = track.GetChisquare()
        ndf = track.GetNDF()

        #draw_track = (chi2 / ndf < 10.)
        draw_track = abs(angle) < 0.05
        #draw_track = True
    
    else:
       draw_track = False

    
    #-----------------------------
    # Find residuals
    
    track_unb_arr_z = {}
    track_unb_arr_y = {}
    track_unb = {}
    chi2_unb = {}
    
    colour = ievent % 50 + 51

    for ip, sector in IPMap.iteritems():
        if sector[2] != 'S':
            continue

        ## residuals wrt pixel track
        try:
            #pix_track_par = pix_tracks[ievent].Fit('pol1', 'SQ0')
            #pix_track = pix_tracks[ievent].GetFunction('pol1')
            residual = ypos[sector] - pix_tracks_func[ievent].Eval(zpos[sector])
            residuals_p[sector].Fill( residual )
            for pix_ievent, pix_event in PixelEvents.iteritems():
                residual = ypos[sector] - pix_tracks_func[pix_ievent].Eval(zpos[sector])
                synch_diagnostic[ip].Fill( ievent - pix_ievent, residual )
        except KeyError:
            pass
        
    if not draw_track:
        continue
        
    for ip, sector in IPMap.iteritems():
        if sector[2] != 'S':
            continue

        ## standalone biased residuals
        residuals_b[sector].Fill( ypos[sector] - track.Eval(zpos[sector]) )
        
        ## standalone unbiased residuals
        track_unb_arr_z[sector] = array.array('d', list(x[0] for x in track_unb_pos[sector]))                                    #
        track_unb_arr_y[sector] = array.array('d', list(x[1] for x in track_unb_pos[sector]))                                    #
        
        tracks_unb[sector].append( ROOT.TGraph(len(track_unb_arr_z[sector]), track_unb_arr_z[sector], track_unb_arr_y[sector]) ) #
        track_unb_par = tracks_unb[sector][-1].Fit('pol1', 'SQ0')                                                                #
        track_unb[sector] = tracks_unb[sector][-1].GetFunction('pol1')                                                           #
        #chi2_unb[sector] = track_unb[sector].GetChisquare()                                                                     #
        #ndf_unb[sector] = track_unb[sector].GetNDF()                                                                            #
                                                                                                                                 #
        residuals[sector].Fill( ypos[sector] - track_unb[sector].Eval(zpos[sector]) )                                            #

        #-----------------------------
        # Draw the tracks
    
        tracks_unb[sector][-1].SetMarkerColor(colour)
        track_unb[sector].SetLineColor(colour)
        
        ipad = int(sector[1])    
        Canvas['T'].cd( ipad )
        tracks_unb[sector][-1].Draw('Psame')
        track_unb[sector].Draw('Lsame')

    tracks[ievent].SetMarkerColor(colour)
    track.SetLineColor(colour)    
    
    tracks_Canvas.cd()
    tracks[ievent].Draw('Psame')
    track.Draw('Lsame')
    
    comb_tracks_Canvas.cd()
    tracks[ievent].Draw('Psame')
    track.Draw('Lsame')


#-----------------------------
# Plot the tracks

tracks_Canvas.Print( outDir + 'tracks.png' )
Canvas['T'].Print( outDir + 'tracks_unb.png' )
comb_tracks_Canvas.Print( outDir + 'comb_tracks.png' )


#-----------------------------
# Plot the angles

square_Canvas.cd()

#ROOT.gStyle.SetOptStat('emrou')  ## 'eMRou'
#ROOT.gStyle.SetOptFit(111)
ROOT.gStyle.SetOptStat('e')
ROOT.gStyle.SetOptFit(111)
square_Canvas.Clear('D')

angles.SetMaximum( angles.GetMaximum() * 1.5 )
angles.GetXaxis().SetTitle( "Track angle [mrad]" )
angles.GetYaxis().SetTitle( "Events" )
angles.Draw('hist')

if angles.GetEntries() != 0:
    angles_fit = angles.Fit('gaus','S')
    angles_mygauss = angles.GetFunction('gaus')
    angles_mygauss.SetLineColor(2)    
    angles_mygauss.Draw('same')
    
square_Canvas.Print( outDir + 'angles.png' )


#-----------------------------
# Plot the cutflow

ROOT.gStyle.SetOptStat('eou')
ROOT.gStyle.SetOptFit(0)
    
Canvas['P'].Clear('D')
Canvas['S'].Clear('D')

for ip, sector in IPMap.iteritems():
    if sector[2] != 'S':
        continue
    ipad = int(sector[1])    
    Canvas[ps].cd( ipad )
    
    cutflow[ip].GetXaxis().SetTitle( sector + " cutflow" )
    cutflow[ip].GetYaxis().SetTitle( "Events" )
    cutflow[ip].Draw('hist')
                
Canvas['P'].Print( outDir + 'cutflow_P.png' )
Canvas['S'].Print( outDir + 'cutflow_S.png' )


#-----------------------------
# Plot the sector correlations for selected events

ROOT.gStyle.SetPaintTextFormat('.0f');

square_Canvas.cd()
sector_corr_sel.GetXaxis().SetTitle( "2D: Occupancy for selected events" )
sector_corr_sel.GetZaxis().SetTitle( "Events" )
sector_corr_sel.SetMinimum( 0. )
sector_corr_sel.Draw('COLZTEXT')

square_Canvas.Print( outDir + 'sector_corr_selected.png' )


#-----------------------------
# Plot the synchronization diagnostic

ROOT.gStyle.SetOptStat('e')
ROOT.gStyle.SetOptFit(0)
    
Canvas['S'].Clear('D')

for ip, sector in IPMap.iteritems():
    if sector[2] != 'S':
        continue
    ipad = int(sector[1])    
    Canvas[ps].cd( ipad )
    
    synch_diagnostic[ip].GetXaxis().SetTitle( "#Delta trigger number" )
    synch_diagnostic[ip].GetYaxis().SetTitle( sector + " residuals wrt pixel [mm]" )
    synch_diagnostic[ip].GetZaxis().SetTitle( "Events" )
    synch_diagnostic[ip].Draw('COLZ')

Canvas['S'].Print( outDir + 'synch_diagnostic_S.png' )



#-----------------------------
# Vladimir Petrovich

latex = ROOT.TLatex()
latex.SetNDC(1)
latex.SetTextAlign(13)
latex_xpos = 0.2
latex_ypos = 0.9

msize = 0.3
mstyle = 7

Canvas['Y'].Clear('D')

ydiag['1S2S'].GetXaxis().SetTitle( "L1S3" )
ydiag['1S2S'].GetYaxis().SetTitle( "L2S3" )
ydiag['1S3S'].GetXaxis().SetTitle( "L1S3" )
ydiag['1S3S'].GetYaxis().SetTitle( "L3S3" )
ydiag['1S4S'].GetXaxis().SetTitle( "L1S3" )
ydiag['1S4S'].GetYaxis().SetTitle( "L4S3" )
ydiag['3S2S'].GetXaxis().SetTitle( "L3S3" )
ydiag['3S2S'].GetYaxis().SetTitle( "L2S3" )
ydiag['2S4S'].GetXaxis().SetTitle( "L2S3" )
ydiag['2S4S'].GetYaxis().SetTitle( "L4S3" )
ydiag['3S4S'].GetXaxis().SetTitle( "L3S3" )
ydiag['3S4S'].GetYaxis().SetTitle( "L4S3" )

for DblS, iDblS in DblSMap.iteritems():
    if ydiag[DblS].GetN() != 0:
        Canvas['Y'].cd( iDblS )
        ydiag[DblS].SetMarkerSize(msize)
        ydiag[DblS].SetMarkerStyle(mstyle)
        ydiag[DblS].Draw('AP')
        corr = ydiag[DblS].GetCorrelationFactor()
        latex.DrawLatex( latex_xpos, latex_ypos, "#rho = %.4f"%(corr) )

Canvas['Y'].Print( outDir + 'ypos_graph.png' )

Canvas['S'].Clear('D')
for ip, sector in IPMap.iteritems():
    if sector[2] != 'S':
        continue
    ipad = int(sector[1])    
    Canvas[ps].cd( ipad )

    ydiag_sil[sector].GetXaxis().SetTitle( sector + " y [mm]" )
    ydiag_sil[sector].GetYaxis().SetTitle( "Pixel track y [mm]" )
    ydiag_sil[sector].SetMarkerSize(msize)
    ydiag_sil[sector].SetMarkerStyle(mstyle)
    ydiag_sil[sector].Draw('AP')
    corr = ydiag_sil[sector].GetCorrelationFactor()
    latex.DrawLatex( latex_xpos, latex_ypos, "#rho = %.4f"%(corr) )

Canvas['S'].Print( outDir + 'ypos_graph_sil.png' )


print
print "Fitting sine waves"

Canvas['Y'].Clear('D')

ysin['1S2S'].GetYaxis().SetTitle( "L1S3 - L2S3" )
ysin['1S2S'].GetXaxis().SetTitle( "L1S3" )
ysin['1S3S'].GetYaxis().SetTitle( "L1S3 - L3S3" )
ysin['1S3S'].GetXaxis().SetTitle( "L1S3" )
ysin['1S4S'].GetYaxis().SetTitle( "L1S3 - L4S3" )
ysin['1S4S'].GetXaxis().SetTitle( "L1S3" )
ysin['3S2S'].GetYaxis().SetTitle( "L3S3 - L2S3" )
ysin['3S2S'].GetXaxis().SetTitle( "L3S3" )
ysin['2S4S'].GetYaxis().SetTitle( "L2S3 - L4S3" )
ysin['2S4S'].GetXaxis().SetTitle( "L2S3" )
ysin['3S4S'].GetYaxis().SetTitle( "L3S3 - L4S3" )
ysin['3S4S'].GetXaxis().SetTitle( "L3S3" )

# c + a*sin(b*(x-d))

latex_xpos_a = 0.2
latex_xpos_b = 0.5
latex_xpos_c = 0.2
latex_xpos_d = 0.5
latex_ypos_a = 0.9
latex_ypos_b = 0.9
latex_ypos_c = 0.85
latex_ypos_d = 0.85

Canvas['Y'].Clear('D')
for DblS, iDblS in DblSMap.iteritems():
    print DblS
    if ysin[DblS].GetN() != 0:
        Canvas['Y'].cd( iDblS )
        ysin[DblS].SetMarkerSize(msize)
        ysin[DblS].SetMarkerStyle(mstyle)
        ysin[DblS].GetYaxis().SetRangeUser(-1.0, 0.5)
        ysin[DblS].Draw('AP')
    
        ysin_func[DblS] = ROOT.TF1("ysin_func_" + DblS, "[0]+[1]*sin(6.2831858*([2]*x-[3]))", -1.0, 0.5)
        ysin_func[DblS].SetLineColor(2)
        ysin_func[DblS].SetParameters(-0.5, 0.2, 1., 0.)
        ysin_func[DblS].SetParLimits(0, -1., 0.5)
        ysin_func[DblS].SetParLimits(1, 0., 0.4)
        ysin_func[DblS].SetParLimits(2, 0.5, 1.5)
        ysin_func[DblS].SetParLimits(3, 0., 1.)
        ysin_fit[DblS] = ysin[DblS].Fit(ysin_func[DblS],'S')
        sin_c = ysin_func[DblS].GetParameter(0)
        sin_a = ysin_func[DblS].GetParameter(1)
        sin_b = ysin_func[DblS].GetParameter(2)
        sin_d = ysin_func[DblS].GetParameter(3)
        latex.DrawLatex( latex_xpos_c, latex_ypos_c, "c = %.3f"%(sin_c) )
        latex.DrawLatex( latex_xpos_a, latex_ypos_a, "a = %.3f"%(sin_a) )
        latex.DrawLatex( latex_xpos_b, latex_ypos_b, "b = %.3f"%(sin_b) )
        latex.DrawLatex( latex_xpos_d, latex_ypos_d, "d = %.3f"%(sin_d) )        
        ysin_func[DblS].Draw('same')

Canvas['Y'].Print( outDir + 'ysin_graph.png' )

Canvas['S'].Clear('D')
for ip, sector in IPMap.iteritems():
    if sector[2] != 'S':
        continue
    ipad = int(sector[1])    
    Canvas[ps].cd( ipad )

    print sector
    if ysin_sil[sector].GetN() != 0:
        ysin_sil[sector].GetYaxis().SetTitle( sector + " y - Pixel track y [mm]" )
        ysin_sil[sector].GetXaxis().SetTitle( sector + " y [mm]" )
        ysin_sil[sector].SetMarkerSize(msize)
        ysin_sil[sector].SetMarkerStyle(mstyle)
        ysin_sil[sector].GetYaxis().SetRangeUser(-5., 5.)
        ysin_sil[sector].Draw('AP')
        
        ysin_sil_func[sector] = ROOT.TF1("ysin_sil_func_" + sector, "[0]+[1]*sin(6.2831858*([2]*x-[3]))", -1.0, 0.5)
        ysin_sil_func[sector].SetLineColor(2)
        ysin_sil_func[sector].SetParameters(-0.5, 0.2, 1., 0.)
        ysin_sil_func[sector].SetParLimits(0, -1., 0.5)
        ysin_sil_func[sector].SetParLimits(1, 0., 0.4)
        ysin_sil_func[sector].SetParLimits(2, 0.5, 5.)
        ysin_sil_func[sector].SetParLimits(3, 0., 1.)
        ysin_sil_fit[sector] = ysin_sil[sector].Fit(ysin_sil_func[sector],'S')
        sin_c = ysin_sil_func[sector].GetParameter(0)
        sin_a = ysin_sil_func[sector].GetParameter(1)
        sin_b = ysin_sil_func[sector].GetParameter(2)
        sin_d = ysin_sil_func[sector].GetParameter(3)
        latex.DrawLatex( latex_xpos_c, latex_ypos_c, "c = %.3f"%(sin_c) )
        latex.DrawLatex( latex_xpos_a, latex_ypos_a, "a = %.3f"%(sin_a) )
        latex.DrawLatex( latex_xpos_b, latex_ypos_b, "b = %.3f"%(sin_b) )
        latex.DrawLatex( latex_xpos_d, latex_ypos_d, "d = %.3f"%(sin_d) )        
        ysin_sil_func[sector].Draw('same')

Canvas['S'].Print( outDir + 'ysin_graph_sil.png' )


print
print "Fitting Vladimir's residuals"

ROOT.gStyle.SetOptStat('emrou')  ## 'eMRou'
ROOT.gStyle.SetOptFit(111)
Canvas['Y'].Clear('D')

yrot['1S2S'].GetXaxis().SetTitle( "L1S3 - L2S3" )
yrot['1S2S'].GetYaxis().SetTitle( "Events" )
yrot['1S3S'].GetXaxis().SetTitle( "L1S3 - L3S3" )
yrot['1S3S'].GetYaxis().SetTitle( "Events" )
yrot['1S4S'].GetXaxis().SetTitle( "L1S3 - L4S3" )
yrot['1S4S'].GetYaxis().SetTitle( "Events" )
yrot['3S2S'].GetXaxis().SetTitle( "L3S3 - L2S3" )
yrot['3S2S'].GetYaxis().SetTitle( "Events" )
yrot['2S4S'].GetXaxis().SetTitle( "L2S3 - L4S3" )
yrot['2S4S'].GetYaxis().SetTitle( "Events" )
yrot['3S4S'].GetXaxis().SetTitle( "L3S3 - L4S3" )
yrot['3S4S'].GetYaxis().SetTitle( "Events" )

for DblS, iDblS in DblSMap.iteritems():
    print DblS
    if yrot[DblS].GetEntries() != 0:
        Canvas['Y'].cd( iDblS )
        yrot[DblS].Draw('hist')
        ROOT.gPad.Update()
        yrot_fit[DblS] = yrot[DblS].Fit('gaus','S')
        yrot_func[DblS] = yrot[DblS].GetFunction('gaus')
        yrot_func[DblS].SetLineColor(2)    
        yrot_amplitude = yrot_func[DblS].GetParameter(0)
        yrot_mean = yrot_func[DblS].GetParameter(1)
        yrot_width = yrot_func[DblS].GetParameter(2)
        latex.DrawLatex( 0.7, 0.9,  "A = %.0f"%(yrot_amplitude) )
        latex.DrawLatex( 0.7, 0.85, "#mu = %.2f"%(yrot_mean) )
        latex.DrawLatex( 0.7, 0.8,  "#sigma = %.3f"%(yrot_width) )
        yrot_func[DblS].Draw('same')

Canvas['Y'].Print( outDir + 'yrot.png' )

Canvas['S'].Clear('D')
for ip, sector in IPMap.iteritems():
    if sector[2] != 'S':
        continue
    ipad = int(sector[1])    
    Canvas[ps].cd( ipad )

    print sector
    if yrot_sil[sector].GetEntries() != 0:
        yrot_sil[sector].GetXaxis().SetTitle( sector + " y - Pixel track y [mm]" )
        yrot_sil[sector].GetYaxis().SetTitle( "Events" )
        yrot_sil[sector].Draw('hist')
        ROOT.gPad.Update()
        yrot_sil_fit[sector] = yrot_sil[sector].Fit('gaus','S')
        yrot_sil_func[sector] = yrot_sil[sector].GetFunction('gaus')
        yrot_sil_func[sector].SetLineColor(2)    
        yrot_sil_amplitude = yrot_sil_func[sector].GetParameter(0)
        yrot_sil_mean = yrot_sil_func[sector].GetParameter(1)
        yrot_sil_width = yrot_sil_func[sector].GetParameter(2)
        latex.DrawLatex( 0.7, 0.9,  "A = %.0f"%(yrot_sil_amplitude) )
        latex.DrawLatex( 0.7, 0.85, "#mu = %.2f"%(yrot_sil_mean) )
        latex.DrawLatex( 0.7, 0.8,  "#sigma = %.3f"%(yrot_sil_width) )
        yrot_sil_func[sector].Draw('same')
    
Canvas['S'].Print( outDir + 'yrot_sil.png' )


#-----------------------------
# Plot the residuals wrt pixel track

ROOT.gStyle.SetOptStat('emrou')  ## 'eMRou'
ROOT.gStyle.SetOptFit(111)
Canvas['S'].Clear('D')

if doPixel:

    for ip, sector in IPMap.iteritems():
        if sector[2] != 'S':
            continue
        ipad = int(sector[1])    
        Canvas['S'].cd( ipad )
        print sector

        residuals_p[sector].SetMaximum( residuals_p[sector].GetMaximum() * 1.5 )
        residuals_p[sector].GetXaxis().SetTitle( sector + " residuals wrt pixel track [mm]" )
        residuals_p[sector].GetYaxis().SetTitle( "Events" )
        residuals_p[sector].Draw('hist')

        if residuals_p[sector].GetEntries() != 0:        
            residuals_p_func[sector] = ROOT.TF1("residuals_p_func_" + sector, 'gaus', -1., 1.)
            residuals_p_func[sector].SetParameters(500., 0., 0.1, 0.)
            residuals_p_func[sector].SetParLimits(1, -1., 1.)
            residuals_p_func[sector].SetParLimits(2, 0.05, 0.3)
            residuals_p_fit = residuals_p[sector].Fit('residuals_p_func_' + sector,'BS')
            residuals_p_func[sector].SetLineColor(2)
            residuals_p_func[sector].Draw('same')

    Canvas['S'].Print( outDir + 'residuals_wrt_pixel.png' )


#-----------------------------
# Plot the biased residuals

ROOT.gStyle.SetOptStat('emrou')  ## 'eMRou'
ROOT.gStyle.SetOptFit(111)
Canvas['S'].Clear('D')

for ip, sector in IPMap.iteritems():
    if sector[2] != 'S':
        continue
    ipad = int(sector[1])    
    Canvas['S'].cd( ipad )
    print sector

    residuals_b[sector].SetMaximum( residuals_b[sector].GetMaximum() * 1.5 )
    residuals_b[sector].GetXaxis().SetTitle( sector + " inclusive residuals [mm]" )
    residuals_b[sector].GetYaxis().SetTitle( "Events" )
    residuals_b[sector].Draw('hist')

    if residuals_b[sector].GetEntries() != 0:
        residuals_b_fit = residuals_b[sector].Fit('gaus','S')
        residuals_b_func[sector] = residuals_b[sector].GetFunction('gaus')
        residuals_b_func[sector].SetLineColor(2)    
        residuals_b_func[sector].Draw('same')

Canvas['S'].Print( outDir + 'residuals_incl.png' )


#-----------------------------
# Plot the unbiased residuals

ROOT.gStyle.SetOptStat('emrou')  ## 'eMRou'
ROOT.gStyle.SetOptFit(111)
Canvas['S'].Clear('D')

for ip, sector in IPMap.iteritems():
    if sector[2] != 'S':
        continue
    ipad = int(sector[1])    
    Canvas['S'].cd( ipad )
    print sector

    residuals[sector].SetMaximum( residuals[sector].GetMaximum() * 1.5 )
    residuals[sector].GetXaxis().SetTitle( sector + " residuals [mm]" )
    residuals[sector].GetYaxis().SetTitle( "Events" )
    residuals[sector].Draw('hist')

    if residuals[sector].GetEntries() != 0:
        residuals_fit = residuals[sector].Fit('gaus','S')
        residuals_func[sector] = residuals[sector].GetFunction('gaus')
        residuals_func[sector].SetLineColor(2)    
        residuals_func[sector].Draw('same')

Canvas['S'].Print( outDir + 'residuals.png' )


#-----------------------------
# Plot the event_hist cluster means

print
print "Fitting event means"

ROOT.gStyle.SetOptStat('eM')
ROOT.gStyle.SetOptFit(111)
Canvas['S'].Clear('D')

for ip, sector in IPMap.iteritems():
    if sector[2] != 'S':
        continue
    ps = sector[2]
    ipad = int(sector[1])    
    Canvas['E'].cd( ipad )
    print sector
    
    event_hist_means[ip].SetMaximum( event_hist_means[ip].GetMaximum() * 1.5 )
    if sector[1:3] in ['2S','3S']:
        event_hist_means[ip].GetXaxis().SetTitle( "63 - Cluster Means, " + sector + " channels" )
    else:
        event_hist_means[ip].GetXaxis().SetTitle( "Cluster Means, " + sector + " channels" )
    event_hist_means[ip].GetYaxis().SetTitle( "Events" )
    event_hist_means[ip].Draw('hist')

    if event_hist_means[ip].GetEntries() != 0:
        event_means_fit = event_hist_means[ip].Fit('gaus','S')
        e_means_mygauss = event_hist_means[ip].GetFunction('gaus')
        e_means_mygauss.SetLineColor(2)    
        e_means_mygauss.Draw('same')

Canvas['E'].Print( outDir + 'event_means.png' )


