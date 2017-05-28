#Global variables
Aactive = 691.8
Bactive = 1040.4
OpenAngleDegree = 0.5*17
H1active = 2246.8
H2active = 3413.2
Achamber = 741.1
H1chamber = 2235.8
Apads = 677.6
Bpads = 1026.3

#For Strips
FirstStrip = 28
WidthStrip = 3.2
NbStrips = 365

#For Pads
APads = 677.6
AngleFirstColumnDegree = 3.75
NbRaw = 15
NbColumn = [2,2,3,3]
ExtraShift = [2.0,-2.0,2.0,-2.0]
PadHeight = 80
FirstRawHeight = [93.2,93.2,60.2,60.2]
LastRawHeight = [33.2,33.2,63.0,63.0]


#------------------------------------------------------------

#Get absolute Strip number relative to Strip 0 (eg. first Strip of L1S1 will be 28, last strip of L1S5 will be 348)
def ChannelToStrip( Channel, VMM ):
    Layer = int(VMM[1])
    Connector = int(VMM[3])
    if Layer == 1 or Layer == 4:
        return FirstStrip + Channel + 64 * ( Connector - 1 )
    elif Layer == 2 or Layer == 3:
        return FirstStrip + ( 63 - Channel ) + 64 * ( Connector - 1 )
    else:
        print('Error: Invalid layer number')
        return -1

#------------------------------------------------------------

#Returns absolute y position (mm) of strip layer w.r.t. bottom of TGC
def PositionStrip( Channel, VMM ):
    Layer = int(VMM[1])
    StripNumber = ChannelToStrip( Channel, VMM )
    if StripNumber < 0:
        print( 'Error: Invalid layer number' )
        return -1
    firstPosition = [0.5*WidthStrip, 0.25*WidthStrip]  # 2,4 : 1,3
    lastPosition = [ (H2active - H1active) - 0.25*WidthStrip, (H2active - H1active) - 0.5*WidthStrip ]
    if StripNumber == 1:
        return firstPosition[Layer%2] + (H1active - H1chamber)
    if StripNumber == NbStrips:
        return lastPosition[Layer%2] + (H1active - H1chamber)
    secondPosition = [ 1.5*WidthStrip, WidthStrip ]
    position = secondPosition[Layer%2] + WidthStrip * (StripNumber - 2) + (H1active - H1chamber)
    return position


