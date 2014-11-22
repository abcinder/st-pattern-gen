import time
import ConfigParser
import argparse
from configobj import ConfigObj
import logging
import EagleCLI as eCLI #Eagle Command Line Interface module
import afunc as aFUN #Anton's misc. functions

#Create logger
logLevel = logging.INFO
logging.basicConfig(format='%(levelname)s - %(message)s', level=logLevel)

#Get .ini filename from command line input
parser = argparse.ArgumentParser()
parser.add_argument('cfg')
args = parser.parse_args()
CONFIGURATION_FILE_NAME = args.cfg

#Create ConfigObj
config = ConfigObj(file_error=True)
config.filename = CONFIGURATION_FILE_NAME
config.reload()

#Check .ini file
if config['type'] == 'driver':
    logging.debug('Valid .ini file.')
else:
    logging.error('Invalid .ini file. ' + 'Driver type found: ' + config['type'])

#Load .ini file
SCRIPT_NAME = str(config['name']['scriptName'])
logging.info('Design: ' + SCRIPT_NAME)
SCRIPT_PATH = str(config['name']['scriptPath'])

DRIVER_POINTS = int(config['driver']['touchPoints'])
DRIVER_SIDES = int(config['driver']['sides'])
DRIVER_ROWS = int(config['driver']['row'])
DRIVER_COLUMNS = int(config['driver']['col'])
logging.info('Points: ' + str(DRIVER_POINTS))
logging.info('Sides: ' + str(DRIVER_SIDES))
logging.info('Rows: ' + str(DRIVER_ROWS))
logging.info('Columns: ' + str(DRIVER_COLUMNS))
DRIVER_IC = str(config['driver']['IC'])
DRIVER_RELAY = str(config['driver']['relay'])
DRIVER_CONNECTOR = str(config['driver']['conn'])
logging.info('IC: ' + DRIVER_IC)
logging.info('Relay: ' + DRIVER_RELAY)
logging.info('Connector: ' + DRIVER_CONNECTOR)

COPPER_POUR = float(config['board']['pour']) #oz
TRACE_WIDTH = float(config['board']['traceWidth']) #in
TRACE_SPACING = float(config['board']['traceSpacing']) #in
BOARD_THICKNESS = float(config['board']['thickness']) #in
logging.info('Trace Width: ' + str(TRACE_WIDTH))
logging.info('Trace Spacing: ' + str(TRACE_SPACING))
logging.info('Board Thickness: ' + str(BOARD_THICKNESS))
logging.info('Copper Pour: ' + str(COPPER_POUR) + ' OZ')

FINGER_FINISH = str(config['finger']['finish']) #in
FINGER_WIDTH = float(config['finger']['width']) #in
FINGER_HEIGHT = float(config['finger']['height']) #in
FINGER_PITCH = float(config['finger']['pitch']) #in
logging.info('Finger Finish: ' + FINGER_FINISH)
logging.info('Finger Width: ' + str(FINGER_WIDTH))
logging.info('Finger Height: ' + str(FINGER_HEIGHT))
logging.info('Finger Pitch: ' + str(FINGER_PITCH))
FINGER_TOPCLEARANCE = float(config['finger']['topClearance']) #in
FINGER_EDGE_TO_ORIGIN = float(config['finger']['sideEdgeToPadOrigin']) #in
FINGER_SIDECLEARANCE = float(config['finger']['sideClearance']) #in
if FINGER_SIDECLEARANCE != FINGER_EDGE_TO_ORIGIN - FINGER_WIDTH/2:
    logging.error('sideClearance != sideEdgeToPadOrigin')
FINGER_BEVEL = float(config['finger']['bevelHeight']) #in
FINGER_POLARIZED = aFUN.parseBooleanString(config['finger']['polarized']) #boolean
FINGER_CUT_LOC = float(config['finger']['cutLoc'])
FINGER_CUT_WIDTH = float(config['finger']['cutWidth']) #in
FINGER_CUT_DEPTH = float(config['finger']['cutDepth']) #in
logging.info('Polarized: ' + str(FINGER_POLARIZED))
if FINGER_POLARIZED:
    logging.info('Cut Location: ' + str(FINGER_CUT_LOC))
    logging.info('Cut Width: ' + str(FINGER_CUT_WIDTH))
    logging.info('Cut Depth: ' + str(FINGER_CUT_DEPTH))

''' DRIVER SPECIFIC FUNCTIONS '''

    
''' CREATE EAGLE SCRIPT '''
#Open .scr file
out = aFUN.openFile(SCRIPT_NAME + '.scr')

out.write(eCLI.setVectorFont())
out.write(eCLI.clearBoard())
out.write(eCLI.createAllCustomLayers())

out.write(eCLI.grid(unit='in', value=0.006, toggle='on'))
out.write(eCLI.goldFingerDimensions(pads=DRIVER_POINTS,
    padW=FINGER_WIDTH,
    padH=FINGER_HEIGHT,
    padP=FINGER_PITCH,
    top=FINGER_TOPCLEARANCE,
    side=FINGER_SIDECLEARANCE,
    bevel=FINGER_BEVEL))
out.write(eCLI.goldFingerPads(pads=DRIVER_POINTS,
    padW=FINGER_WIDTH,
    padH=FINGER_HEIGHT,
    padP=FINGER_PITCH,
    top=FINGER_TOPCLEARANCE,
    side=FINGER_SIDECLEARANCE,
    bevel=FINGER_BEVEL))

RELAY_CLEARANCE = 1.00

out.write(eCLI.placeDriver(0, RELAY_CLEARANCE))

out.write(eCLI.window('FIT'))

#Close file
aFUN.closeFile(out)

#Run Eagle script
eCLI.runScript(0.5, SCRIPT_PATH, SCRIPT_NAME + '.scr')

#Remove generated Eagle script. These just add clutter. Just keep the .ini files.
time.sleep(3) #Delay needed to let Eagle process the script before it is deleted.
# aFUN.removeFile(SCRIPT_PATH + SCRIPT_NAME + '.scr')