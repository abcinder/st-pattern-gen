import pygtk
pygtk.require('2.0')
import time
import math
import os, sys
import re
import gtk
import wnck
from pykeyboard import PyKeyboard
from pymouse import PyMouse
import ConfigParser
import argparse
from operator import itemgetter
from configobj import ConfigObj
import commands #for detecting caps lock
import afunc #Anton's functions
import EagleCLI as eCLI
import stParameters as stPARA

DELAY = 0.5

''' MISC FUNCTIONS '''

def multikeysort(items, columns):
    #from operator import itemgetter
    comparers = [ ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]
    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)

def pipDict(x, y, poly):
    n = len(poly)
    inside = False
    
    p1x,p1y = poly[0]['x'], poly[0]['y']
    for i in range(n+1):
        p2x,p2y = poly[i % n]['x'], poly[i % n]['y']
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside
        
def runScript(delay, SCRIPT_PATH, SCRIPT_NAME):
    screen = wnck.screen_get(0)
    #screen = wnck.screen_get_default()

    while gtk.events_pending():
        gtk.main_iteration()

    windowTitle = re.compile('.*Board.*')
    
    for window in screen.get_windows():
        if windowTitle.match(window.get_name()):
            window.activate(int(time.time()))
            window.maximize()
    
    #MOUSE CLICK TO ACTUALLY FOCUS EAGLE BOARD
    m = PyMouse()
    x, y = m.screen_size()
    #m.click(x/4, y/4, 1)
    
    #KEYBOARD INPUT
    k = PyKeyboard()
    
    caps_flag = 0
    if int(commands.getoutput('xset q | grep LED')[65]) % 2:
        k.tap_key(k.caps_lock_key)
        caps_flag = 1
    
    #BRING UP ALT-FILE MENU
    k.press_key(k.alt_key)
    k.type_string('f')
    k.release_key(k.alt_key)
    
    #PRESS T TO RUN SCRIPT FROM ALT-FILE MENUs
    k.type_string('t')
    
    time.sleep(delay)
    
    #TYPE IN SCRIPT NAME TO DIALOG BOX
    k.type_string(SCRIPT_PATH + SCRIPT_NAME)
    
    time.sleep(delay)
    time.sleep(delay)
    
    k.tap_key(k.enter_key)
    
    if caps_flag:
        k.tap_key(k.caps_lock_key)

    
''' EXPLICIT EAGLE FUNCTIONS '''

#def add(dev, lib, r='0', x=0, y=0):
    #out.write('ADD ' + str(dev) + '@' + str(lib) + ' R' + str(r) + ' (' + str(x) + ' ' + str(y) + ')\r\n')

def add(name, pkg, lib, r='0', x=0, y=0):
    out.write("ADD '" + str(name) + "' " + str(pkg) + "[@" + str(lib) + "]\r\n")
    click('left', x, y)

def addPkg(pkg, lib, r='0', x=0, y=0):
    out.write('add '+str(pkg)+'@'+str(lib)+' R'+str(r)+' ('+str(x)+' '+str(y)+')\r\n')
    
def click(button, x=0, y=0):
    if button == 'left':
        out.write('(' + str(x) + ' ' + str(y) + ')\r\n')   #left click
    elif button == 'right':
        out.write('(>' + str(x) + ' ' + str(y) + ')\r\n')  #right click
    else:
        print 'error in click button input'
    
def close():
    out.write('CLOSE\r\n')
    
def setSize(size):
    grid()
    out.write('CHANGE SIZE ' + str(size) + '\r\n')
    
def change_pour(param='solid'):
    grid()
    out.write('CHANGE POUR ' + str(param) + '\r\n')
    #CHANGE POUR SOLID | HATCH
    
def change_spacing(value):
    grid()
    out.write('CHANGE SPACING ' + str(value) + '\r\n')
    
def setDrill(value, unit='mm'):
    grid(unit)
    out.write('CHANGE DRILL ' + str(value) + '\r\n')
    grid()
    
def circlePoly(x, y, r, width=0.01):
    function = 'poly'
    net = 'ito'
    #poly gnd (P 10 0) +180 (P 10 180) +180 (P 10 0);
    
    out.write(function + ' ' + net + ' ' + str(width) + ' ' \
        '(' + str(x-(r)) + ' ' + str(y) + ')' + \
        '(' + str(x+(r)) + ' ' + str(y) + ')' + \
        ' +180 (' + str(x-(r)) + ' ' + str(y) + ')\r\n')

    out.write(function + ' ' + net + ' ' + str(width) + ' ' \
        '(' + str(x-(r)) + ' ' + str(y) + ')' + \
        '(' + str(x+(r)) + ' ' + str(y) + ')' + \
        ' -180 (' + str(x-(r)) + ' ' + str(y) + ')\r\n')

def circlePoly_v2(x, y, r, lineWidth=0.01):
    function = 'poly'
    net = 'ito'
    #poly gnd (P 10 0) +180 (P 10 180) +180 (P 10 0);

    out.write(function + ' ' + net + ' ' + str(width) + ' ' \
        '(' + str(x-(r)) + ' ' + str(y) + ')' + \
        '(' + str(x+(r)) + ' ' + str(y) + ')' + \
        ' +180 (' + str(x-(r)) + ' ' + str(y) + ')\r\n')

    out.write()
        
def create_pad(w, h, r, name, x, y):
    out.write('SMD ' + str(W) + ' ' + str(H) + ' ' + str(-1*r) + " '" + str(name) + "' (" + str(x) + ' ' + str(y) + ')\r\n')
    
def delete(x, y, button):
    if str(button).lower() == 'l':
        out.write('DELETE\r\n')
        click('left', x, y)
    elif str(button).lower() == 'r':
        out.write('DELETE\r\n')
        click('right', x, y)
    else:
        print 'INVALID DELETE "CLICK" PARAMETER'

def display(l):
    out.write('DISPLAY ' + str(l) + '\r\n')

def edit(filename):
    out.write('EDIT ' + str(filename) + '\r\n')

def grid(unit='mm', value=0.5, toggle='on'):
    out.write('GRID ' + str(unit) + ' ' + str(value) + ' ' + str(toggle) + '\r\n') 
    
def group(s):
    s = str(s)
    out.write('GROUP (-'+s+' -'+s+') ('+s+' -'+s+') ('+s+' '+s+') (-'+s+' '+s+') (-'+s+' -'+s+')\r\n')
    
def layer(num, name=''):
    out.write('LAYER ' + str(num) + ' ' + str(name) + '\r\n')
    
def move(e, x, y):
    out.write('MOVE ' + str(e) + ' ('+str(x)+' '+str(y)+ ')\r\n')
    
def net(x1, y1, x2, y2, name='\b'):
    out.write('NET ' + name + '('+str(x1)+' '+str(y1)+') ('+str(x2)+' '+str(y2)+')\r\n')
    
def openLibrary(lib):
    out.write('OPEN ' + str(lib) + '\r\n')

def remove(filename):
    out.write('REMOVE ' + str(filename) + '\r\n')

def removeDevice(dev):
    out.write('REMOVE ' + str(dev) + '.dev\r\n')
    
def removePackage(pac):
    out.write('REMOVE ' + str(pkg) + '.pac\r\n')
    
def removeSymbol(sym):
    out.write('REMOVE ' + str(sym) + '.sym\r\n')
   
def rotate(e, r): #can also use to mirror, e.g. angle='MR90'
    out.write('ROTATE ' + str(r) + ' ' + str(e) + '\r\n')

def route(x1, y1, x2, y2):
    out.write('ROUTE ('+str(x1)+' '+str(y1)+') ('+str(x2)+' '+str(y2)+')\r\n')

def script(scr):
    out.write('SCRIPT ' + str(scr) + '.scr\r\n')

def set(parameter, value):
    out.write('SET ' + str(parameter) + ' ' + str(value) + '\r\n')

def setWireBend(value):
    set('WIRE_BEND', value)
    # SET WIRE_BEND bend_number;
    # bend_nr can be one of:
    # 0: Starting point - horizontal - vertical - end
    # 1: Starting point - horizontal - 45 - end
    # 2: Starting point - end (straight connection)
    # 3: Starting point - 45 - horizontal - end
    # 4: Starting point - vertical - horizontal - end
    # 5: Starting point - arc - horizontal - end
    # 6: Starting point - horizontal - arc - end
    # 7: "Freehand" (arc that fits to wire at start, straight otherwise)
    
def signal(net, part1, pin1, part2, pin2): #can only be used on board
    out.write('SIGNAL ' + net + ' ' + part1 + ' ' + pin1 + ' ' + part2 + ' ' + pin2 + '\r\n')
    
def text(string, x, y, size=1, layerNum=21, orientation=''):
    layer(layerNum) #tDocu
    setVectorFont()
    grid()
    setSize(size)
    out.write('TEXT ' + str(string) + ' ' + str(orientation) + '\r\n')
    click('left', x, y)
    
def update(library):
    out.write('UPDATE ' + str(library) + '\r\n')

def via_noNet(x, y, drill=10, unit= 'mil', diameter='0', shape='round', layer1=1, layer2=16):
    setDrill(drill, unit)
    out.write('VIA ' + str(diameter) + ' ' + str(shape) + ' ' + str(layer1) + '-' + str(layer2) + '\r\n')
    click('left', x, y)
    grid()
    
def window(zoom):
    out.write('WINDOW ' + str(zoom) + '\r\n')
    
def wire(x1, y1, x2, y2, width=0.1):
    out.write('WIRE ' + str(width) +
                ' (' + str(x1) + ' ' + str(y1) + ')'+
                ' (' + str(x2) + ' ' + str(y2) + ')'+ '\r\n')

def write(): #aka SAVE
    out.write('WRITE\r\n')


''' EAGLE MACROS '''

def changeSMD(w, h, size=0.5):
    grid(unit='mm', value=0.5, toggle='on')
    out.write('GROUP (-1 -1) (1 -1)(1 1) (-1 1) (-1 -1)\r\n')
    out.write('CHANGE SMD ' + str(w) + ' ' + str(h) + ' (> 0 0)\r\n')
    out.write('DISPLAY NONE\r\n')
    out.write('DISPLAY tPlace\r\n')
    group(800)
    delete(0,0,'r')
    out.write('TEXT >NAME (' + str(-(w/2)-size*(2)) + ' ' + str((h/2)+(size/2)+(0.1*h)) + ')\r\n')
    group(800)
    out.write('CHANGE SIZE ' + str(size) + ' (' + str(-(w/2)-size) + ' ' + str(-size/2) + ')\r\n')
    out.write('DISPLAY ALL\r\n')
    
def setPadPour(pour, spacing='1'):
    change_pour(pour)
    if str(pour) == 'hatch':
        change_spacing(spacing)
    
def clearDrawing(size):
    grid(unit='mm', value=0.5, toggle='on')
    display('ALL')
    group(size)
    delete(0,0,'r')  

def clearSchematic():
    switchToSchematic()
    clearDrawing(2000)
    
def clearBoard():
    switchToBoard()
    clearDrawing(2000)
    
def drawCirclePoly(x, y, radius, width=0.01, unit='mm'):
    grid(unit=unit, value=0.5, toggle='on')
    circlePoly(x, y, radius, width)
    
def drawPolygon(x, y, w, h):
    function = 'poly'
    net = 'ito'
    width = '0.01'
    out.write(function + ' ' + net + ' ' + width + ' ' \
        '(' + str(x-(0.5*w)) + ' ' + str(y-(0.5*h)) + ')' + \
        '(' + str(x+(0.5*w)) + ' ' + str(y-(0.5*h)) + ')' + \
        '(' + str(x+(0.5*w)) + ' ' + str(y+(0.5*h)) + ')' + \
        '(' + str(x-(0.5*w)) + ' ' + str(y+(0.5*h)) + ')' + \
        '(' + str(x-(0.5*w)) + ' ' + str(y-(0.5*h)) + ')\r\n')

def drawDiamond(x, y, w, h):
    function = 'poly'
    net = 'ito'
    width = '0.01'
    #d = float(math.sqrt((w/2)**2 + (h/2)**2))
    out.write(function + ' ' + net + ' ' + width + ' ' \
        '(' + str(x-w/2) + ' ' + str(y) + ')' + \
        '(' + str(x) + ' ' + str(y+h/2) + ')' + \
        '(' + str(x+w/2) + ' ' + str(y) + ')' + \
        '(' + str(x) + ' ' + str(y-h/2) + ')' + \
        '(' + str(x-w/2) + ' ' + str(y) + ')\r\n')
        
def drawPolygonDict(list, l=20, width=0.01):
    layer(l)
    
    for i in range(len(list)):
        x1 = list[i-1]['x']
        y1 = list[i-1]['y']
        x2 = list[i]['x']
        y2 = list[i]['y']
        wire(x1, y1, x2, y2, width)
        
    x0 = list[0]['x']
    y0 = list[0]['y']
    xf = list[len(list)-1]['x']
    yf = list[len(list)-1]['y']
    wire(x0, y0, xf, yf, width)

def fanout(padPerRow, rowCount, dist, pitch, padLength, insideCount, traceWidth, clearance, xo=0, yo=0, r=0, units='mm'):
    layer(TRACE_TOP_LAYER)
    midCount = padPerRow/2
    setWireBend(2) #2: straight
    insideCount += 2
    
    maxInsideCount = int(dist/(clearance*2))
    if insideCount > maxInsideCount:
        insideCount = maxInsideCount
    
    for r in range(rowCount):
        for x in range(padPerRow):
            x += 1

            if x < insideCount-1:
                #INTIAL WIRE
                x1=x*pitch-(pitch/2)-padPerRow/2*pitch
                y1=dist
                x2=x*pitch-(pitch/2)-padPerRow/2*pitch
                y2=dist-padLength/2+traceWidth/2

                if r == 1:
                    y1=-y1
                    y2=-y2

                wire(x1=x1, y1=y1, x2=x2, y2=y2, width=traceWidth)

                #VERTICAL WIRE
                x1=x*pitch-(pitch/2)-padPerRow/2*pitch
                y1=dist+clearance*2
                x2=x*pitch-(pitch/2)-padPerRow/2*pitch
                y2=dist-padLength/2+traceWidth/2-x*(clearance*2)+clearance*2

                if r == 1:
                    y1=-y1
                    y2=-y2

                wire(x1=x1, y1=y1, x2=x2, y2=y2, width=traceWidth)

                #HORZ WIRE
                x1=x*pitch-(pitch/2)-padPerRow/2*pitch
                y1=dist-padLength/2+traceWidth/2-x*(clearance*2)+clearance*2
                x2=x*pitch-(pitch/2)-padPerRow/2*pitch-0.1
                y2=dist-padLength/2+traceWidth/2-x*(clearance*2)+clearance*2

                if r == 1:
                    y1=-y1
                    y2=-y2

                wire(x1=x1, y1=y1, x2=x2, y2=y2, width=traceWidth)

                
                
            elif x > padPerRow-insideCount+2:
                 #INTIAL WIRE
                x1=x*pitch-(pitch/2)-padPerRow/2*pitch
                y1=dist
                x2=x*pitch-(pitch/2)-padPerRow/2*pitch
                y2=dist-padLength/2+traceWidth/2

                if r == 1:
                    y1=-y1
                    y2=-y2

                wire(x1=x1, y1=y1, x2=x2, y2=y2, width=traceWidth)

                #VERTICAL WIRE
                x1=x*pitch-(pitch/2)-padPerRow/2*pitch
                y1=dist
                x2=x*pitch-(pitch/2)-padPerRow/2*pitch
                y2=dist-padLength/2+traceWidth/2-(padPerRow-x)*(clearance*2)

                if r == 1:
                    y1=-y1
                    y2=-y2

                wire(x1=x1, y1=y1, x2=x2, y2=y2, width=traceWidth)

                #VERTICAL WIRE
                x1=x*pitch-(pitch/2)-padPerRow/2*pitch
                y1=dist-padLength/2+traceWidth/2-(padPerRow-x)*(clearance*2)
                x2=x*pitch-(pitch/2)-padPerRow/2*pitch+0.1
                y2=dist-padLength/2+traceWidth/2-(padPerRow-x)*(clearance*2)

                if r == 1:
                    y1=-y1
                    y2=-y2

                wire(x1=x1, y1=y1, x2=x2, y2=y2, width=traceWidth)

                
            else:
                #INTIAL WIRE
                x1=x*pitch-(pitch/2)-padPerRow/2*pitch
                y1=-dist
                x2=x*pitch-(pitch/2)-padPerRow/2*pitch
                y2=-dist-padLength/2+traceWidth/2

                if r == 1:
                    y1=-y1
                    y2=-y2

                wire(x1=x1, y1=y1, x2=x2, y2=y2, width=traceWidth)

                if x <= midCount:
                    #VERTICAL WIRE
                    x1=x*pitch-(pitch/2)-padPerRow/2*pitch
                    y1=-dist-padLength/2+traceWidth/2
                    x2=x*pitch-(pitch/2)-padPerRow/2*pitch
                    y2=-dist-padLength/2+traceWidth/2-(clearance*2*(x-insideCount+1))-clearance*2

                    if r == 0:
                        if insideCount == 0:
                            y2=y2+clearance*6
                    if r == 1:
                        if insideCount == 0:
                            y2=y2+clearance*6
                        y1=-y1
                        y2=-y2

                    wire(x1=x1, y1=y1, x2=x2, y2=y2, width=traceWidth)

                    #HORIZONTAL WIRE
                    x1=x*pitch-(pitch/2)-padPerRow/2*pitch
                    y1=-dist-padLength/2+traceWidth/2-(clearance*2*(x-insideCount+1))-clearance*2
                    x2=x*pitch-(pitch/2)-padPerRow/2*pitch-0.1
                    y2=-dist-padLength/2+traceWidth/2-(clearance*2*(x-insideCount+1))-clearance*2

                    if r == 0:
                        if insideCount == 0:
                            y2=y2+clearance*6
                            y1=y2
                    if r == 1:
                        if insideCount == 0:
                            y2=y2+clearance*6
                            y1=y2
                        y1=-y1
                        y2=-y2

                    wire(x1=x1, y1=y1, x2=x2, y2=y2, width=traceWidth)

                else:
                    #VERTICAL WIRE
                    x1=x*pitch-(pitch/2)-padPerRow/2*pitch
                    y1=-dist-padLength/2+traceWidth/2-(midCount)*clearance*2-(midCount-insideCount-x+2)*clearance*2-clearance*2
                    x2=x*pitch-(pitch/2)-padPerRow/2*pitch
                    y2=-dist-padLength/2+traceWidth/2

                    if r == 0:
                        if insideCount == 0:
                            y1=y1+clearance*6
                    if r == 1:
                        if insideCount == 0:
                            y1=y1+clearance*6
                        y1=-y1                    
                        y2=-y2

                    #if insideCount == 0:
                        #y1=y1-clearance*6

                    wire(x1=x1, y1=y1, x2=x2, y2=y2, width=traceWidth)

                    #HORIZONTAL WIRE
                    x1=x*pitch-(pitch/2)-padPerRow/2*pitch
                    y1=-dist-padLength/2+traceWidth/2-(midCount)*clearance*2-(midCount-insideCount-x+2)*clearance*2-clearance*2
                    x2=x*pitch-(pitch/2)-padPerRow/2*pitch+0.1
                    y2=-dist-padLength/2+traceWidth/2-(midCount)*clearance*2-(midCount-insideCount-x+2)*clearance*2-clearance*2

                    if r == 0:
                        if insideCount == 0:
                            y1=y1+clearance*6
                            y2=y1
                    if r == 1:
                        if insideCount == 0:
                            y1=y1+clearance*6
                            y2=y1
                        y1=-y1
                        y2=-y2

                    wire(x1=x1, y1=y1, x2=x2, y2=y2, width=traceWidth)
    
def setVectorFont(setting='on'):
    set('VECTOR_FONT', setting)
    
def setWireBendStraight():
    setWireBend(2)
    
def switchToBoard():
    edit('.brd')
    
def switchToSchematic():
    edit('.sch')
    
def switchToSheet(x):
    edit('.s' + str(x))
    
def wireBoxWH(w, h, l=20, width=0.01):
    layer(l) # 20 is Dimension layer in Eagle
    wire(-w/2,-h/2,w/2,-h/2, width)
    wire(w/2,-h/2,w/2,h/2, width)
    wire(w/2,h/2,-w/2,h/2, width)
    wire(-w/2,h/2,-w/2,-h/2, width)


''' PATTERN SPECIFIC FUNCTIONS '''

def createAllCustomLayers():
    layer(stPARA.LAYER_TRACE_TOP, 'TRACETOP')
    layer(stPARA.LAYER_TRACE_MID, 'TRACEMID')
    layer(stPARA.LAYER_TRACE_BOT, 'TRACEBOT')
    layer(stPARA.LAYER_TPAD, 'TPAD')
    layer(stPARA.LAYER_TPAD_LABEL, 'TPADLABEL')
    layer(stPARA.LAYER_GRID_TOP, 'TOPGRID')

def drawBoard(routing):

    if setPitch:
        tPts = touchPosSetPitch(col, row, TPAD_SPACING_DIM, pitch, pitch)
    else:
        tPts = touchPos(col, row, TPAD_SPACING_DIM, SCR_W, SCR_H)
    
    if routing == 'side':
        tPt_accum = sideRouteAccum(tPts)
        allPairs = matingPosSide(tPt_accum, TRACE_P)
        drawSide(allPairs, TPAD_W, TPAD_H, TRACE_W)
        
    elif routing == 'grid':
        if gridDisplay:
            drawAllGrids()
        else:
            display(-GRID_TOP_LAYER)
        tPts = sortIntoGrids(tGrid.TT, tPts)
        tPts_accum = gridRouteAccum(tPts)
        pairs = matingPosGrid(tPts_accum, TRACE_P, TPAD_W)
        drawGrid(pairs, TPAD_W, TPAD_H, TRACE_W)
        
    elif routing == 'grid4':
        pass
    else:
        print 'error in routing configuration file params'
    
def drawBorder(w, h, layer=20, width=0.1):
    setWireBendStraight()
    wireBoxWH(w, h, layer, width=0.1)

def drawMilledBorder(barWidth, w, h, row, col, pitch, padDim, l=20, width=0.1):
    layer(20)
    
    colOff = float(0)
    colRange = col-1
    if bool(col % 2) == 0:
        colOff = float(-0.5)
        colRange = col-1
        
    #print bool(col % 2)
    #print (float(col/2) + 0.5)
    #print colOff
    #print float((col/2) + colOff)
        
    rowOff = float(-1)
    rowRange = row-1
    if bool(row % 2) == 0:
        rowOff = float(-1.5)
        rowRange = row-1

    #print bool(row%2)
    #print row%2
    #print (float(row/2) + 0.5)
    #print rowOff
    #print float((row/2) + rowOff)

    for y in range(rowRange):
        for x in range(colRange):
            #inside cross looking box
            wire(   x1=pitch*(x-float(col/2)-colOff)+(barWidth/2),
                    y1=pitch*(y-float(row/2)-rowOff)-padDim/2,
                    #y1=y*pitch-(padDim/2),
                    x2=pitch*(x-float(col/2)-colOff)+(barWidth/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim))
                    #y2=y*pitch-(padDim/2)-(pitch-padDim))

            wire(   x1=pitch*(x-float(col/2)-colOff)+(barWidth/2),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim))

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim)-(padDim/2)+(barWidth/2))

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim)-(padDim/2)+(barWidth/2),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim)-(padDim/2)+(barWidth/2))
                    
            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim)-(padDim/2)+(barWidth/2),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim))

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim)+((padDim-barWidth)/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim))

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim)+((padDim-barWidth)/2),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim)+((padDim-barWidth)/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2))

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim)+((padDim-barWidth)/2),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2))

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)+(padDim-barWidth)/2)

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2)+(padDim-barWidth)/2,
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)+(padDim-barWidth)/2)

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2)+(padDim-barWidth)/2,
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2))

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2),
                    x2=pitch*(x-float(col/2)-colOff)+(barWidth/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2))

            #outside wires
            wire(   x1=pitch*(x-float(col/2)-colOff)-(barWidth/2),
                    y1=pitch*(y-float(row/2)-rowOff)-padDim/2,
                    x2=pitch*(x-float(col/2)-colOff)-(barWidth/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim))

            wire(   x1=pitch*(1+x-float(col/2)-colOff)+(barWidth/2),
                    y1=pitch*(y-float(row/2)-rowOff)-padDim/2,
                    x2=pitch*(1+x-float(col/2)-colOff)+(barWidth/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim))

            wire(   x1=pitch*(-1+x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim),
                    x2=pitch*(-1+x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim)+((padDim-barWidth)/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim))

            wire(   x1=pitch*(1+x-float(col/2)-colOff)+(barWidth/2),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim),
                    x2=pitch*(1+x-float(col/2)-colOff)+(padDim/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim))

            wire(   x1=pitch*(1+x-float(col/2)-colOff)+(barWidth/2),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2),
                    x2=pitch*(1+x-float(col/2)-colOff)+(padDim/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2))
            
            wire(   x1=pitch*(-1+x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y1=pitch*(y-float(row/2)-rowOff)-(padDim/2),
                    x2=pitch*(-1+x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim)+((padDim-barWidth)/2),
                    y2=pitch*(y-float(row/2)-rowOff)-(padDim/2))

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y1=pitch*(1+y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim)-(padDim/2)+(barWidth/2),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y2=pitch*(1+y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim)-(padDim/2)+(barWidth/2))

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y1=pitch*(1+y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y2=pitch*(1+y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim)-(padDim/2)+(barWidth/2))
                    
            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y1=pitch*(-1+y-float(row/2)-rowOff)-(padDim/2),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y2=pitch*(-1+y-float(row/2)-rowOff)-(padDim/2)+(padDim-barWidth)/2)
                    
            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y1=pitch*(-1+y-float(row/2)-rowOff)-(padDim/2),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y2=pitch*(-1+y-float(row/2)-rowOff)-(padDim)+(padDim-barWidth/2))

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y1=pitch*(-1+y-float(row/2)-rowOff)-(padDim/2)+(padDim-barWidth)/2,
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2),
                    y2=pitch*(-1+y-float(row/2)-rowOff)-(padDim/2)+(padDim-barWidth)/2)

            wire(   x1=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y1=pitch*(1+y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim)-(padDim/2)+(barWidth/2),
                    x2=pitch*(x-float(col/2)-colOff)+(padDim/2)+(pitch-padDim),
                    y2=pitch*(1+y-float(row/2)-rowOff)-(padDim/2)-(pitch-padDim))

    #sides and top/bottom
    for y in range(row):
        wire(   x1=-SCR_W/2,
                y1=y*pitch-SCR_H/2,
                x2=-SCR_W/2,
                y2=y*pitch+padDim-SCR_H/2)

        wire(   x1=SCR_W/2,
                y1=y*pitch-SCR_H/2,
                x2=SCR_W/2,
                y2=y*pitch+padDim-SCR_H/2)

    for x in range(col):
        wire(   x1=pitch*(x-float(col/2)-colOff)-padDim*0.5,
                y1=SCR_H/2,
                x2=pitch*(x-float(col/2)-colOff)-padDim*0.5+padDim,
                y2=SCR_H/2)

        wire(   x1=pitch*(x-float(col/2)-colOff)-padDim*0.5,
                y1=-SCR_H/2,
                x2=pitch*(x-float(col/2)-colOff)-padDim*0.5+padDim,
                y2=-SCR_H/2)

def drawAllBorders():
    if MILLED:
        drawMilledBorder(MILLED_WIDTH, SCR_W, SCR_H, row, col, tPadPx, TPAD_H)
    else:
        drawBorder(SCR_W, SCR_H, stPARA.LAYER_TPLACE)
        drawBorder(traceExtW, traceExtH, stPARA.LAYER_TPLACE)
        drawBorder(routeW, routeH, stPARA.LAYER_TPLACE)
        drawBorder(boardW, boardH, stPARA.LAYER_DIMENSION)
    
def drawAllGrids():
    for item in tGrid.TT:
        drawPolygonDict(item, GRID_TOP_LAYER)

def labelBoard():
    #Board title top left corner
    title = config['name']['title']
    text(title, float(-boardW/2+0.5), float(boardH/2-1.5), 1)

    #Row/col/size info bottom left corner
    pad_string = 'R: ' + str(row) + ', C: ' + str(col) + ', SIZE: ' + str(TPAD_H)
    text(pad_string, float(-boardW/2+0.5), float(-boardH/2+0.5), 1)

    #Pad pitch top right
    pad_pitch_string = 'P PITCH- X: ' + str(tPadPx) + ', Y: ' + str(tPadPy)
    text(pad_pitch_string, float(boardW/2-0.5), float(boardH/2-0.5), 1, orientation='R180')

    #Traces info bottom right
    if TRACES_ENABLED:
        trace_string = 'T- W: ' + str(TRACE_W) + ', P: ' + str(TRACE_P)
        text(trace_string, float(boardW/2-0.5), float(-boardH/2+1.5), 1, orientation='R180')

def showTopLayer():
    display(stPARA.TPAD_LAYER)
    display(stPARA.TRACE_TOP_LAYER)
    display(stPARA.GRID_TOP_LAYER)

def touchPos(col, row, padDim, scrW, scrH):
    posList = []
    
    tPadPx = float((scrW-padDim)/(col-1))
    tPadPy = float((scrH-padDim)/(row-1))
    
    for i in range(row):
        y = -scrH/2 + padDim/2 + i*tPadPy
        for j in range(col):
            x = -scrW/2 + padDim/2 + j*tPadPx
            posList.append({'x': x, 'y': y})
    
    return posList

def touchPosSetPitch(col, row, padDim, pitchX, pitchY):
    posList = []
    
    tPadPx = pitchX
    tPadPy = pitchY

    scrW = tPadPx*(col-1) + padDim
    scrH = tPadPy*(row-1) + padDim
    
    for i in range(row):
        y = -scrH/2 + padDim/2 + i*tPadPy
        for j in range(col):
            x = -scrW/2 + padDim/2 + j*tPadPx
            posList.append({'x': x, 'y': y})

    return posList
    
def touchPosOdd(col, row):
    x = 0
    y = 0
    top = []
    bottom = []
    
    xoffset = tPadPx/2
    yoffset = tPadPy/2
    
    for i in range(row):
        y = -SCR_H/2 + TPAD_H/2 + i*tPadPy
        
        for j in range(col):
            x = -SCR_W/2 + TPAD_W/2 + j*tPadPx
              
            if pipRight(x, y):
                if i%2:
                    bottom.append({'x': x, 'y': y})
                else:
                    top.append({'x': x, 'y': y})
            
            if pipTop(x, y):
                if j%2:
                    bottom.append({'x': x, 'y': y})
                else:
                    top.append({'x': x, 'y': y})
            
    for i in range(row):
        y = SCR_H/2 - TPAD_H/2 - i*tPadPy
        
        for j in range(col):
            x = SCR_W/2 - TPAD_W/2 - j*tPadPx
            
            if pipBot(x, y):
                if j%2:
                    bottom.append({'x': x, 'y': y})
                else:
                    top.append({'x': x, 'y': y})
            
            if pipLeft(x, y):
                if i%2:
                    bottom.append({'x': x, 'y': y})
                else:
                    top.append({'x': x, 'y': y})
                           
    return top, bottom            

def touchPosEven(col, row):
    x = 0
    y = 0
    top = []
    bottom = []
    
    xoffset = tPadPx/2
    yoffset = tPadPy/2
    
    #top.append({'x': 0, 'y': 0})
    
    for i in range(row):
        y = i*tPadPy
        if row%2==0:
            y += yoffset
        for j in range(col):
            x = j*tPadPx
            if col%2==0:
                x += xoffset
            
            if x != 0:
                if (j%2):
                    if pipVert(x, y):
                        top.append({'x': x, 'y': y})
                if (j%2==0):
                    if pipVert(x, y):
                        bottom.append({'x': x, 'y': y})
                
                if (i%2==0):
                    if pipHorz(x, y):
                        bottom.append({'x': x, 'y': y})
                if (i%2):
                    if pipHorz(x, y):
                        top.append({'x': x, 'y': y})  

            if y != 0:
                y = -y    
                if (j%2):
                    if pipVert(x, y):
                        top.append({'x': x, 'y': y})
                if (j%2==0):
                    if pipVert(x, y):
                        bottom.append({'x': x, 'y': y})
                
                if (i%2==0):
                    if pipHorz(x, y):
                        bottom.append({'x': x, 'y': y})
                if (i%2):
                    if pipHorz(x, y):
                        top.append({'x': x, 'y': y})
            
            if x != 0:
                x = -x
                
                if (j%2):
                    if pipVert(x, y):
                        top.append({'x': x, 'y': y})
                if (j%2==0):
                    if pipVert(x, y):
                        bottom.append({'x': x, 'y': y})
                
                if (i%2==0):
                    if pipHorz(x, y):
                        bottom.append({'x': x, 'y': y})
                if (i%2):
                    if pipHorz(x, y):
                        top.append({'x': x, 'y': y})
                    
            if y != 0:        
                y = -y   
                
                if (j%2):
                    if pipVert(x, y):
                        top.append({'x': x, 'y': y})
                if (j%2==0):
                    if pipVert(x, y):
                        bottom.append({'x': x, 'y': y})
                
                if (i%2==0):
                    if pipHorz(x, y):
                        bottom.append({'x': x, 'y': y})
                if (i%2):
                    if pipHorz(x, y):
                        top.append({'x': x, 'y': y})   
                
    
    
    
    return top, bottom

def traceLayerAlternator(layer):
    if layer==TRACE_BOT_LAYER:
        return TRACE_MID_LAYER
    elif layer==TRACE_MID_LAYER:
        return TRACE_TOP_LAYER
    elif layer==TRACE_TOP_LAYER:
        return TRACE_BOT_LAYER
    else:
        print 'TRACE LAYER ALTERNATOR INPUT ERROR'
    
def pipVert(x, y):
    if pipDict(x, y, tGrid.TT[0]) or pipDict(x, y, tGrid.TT[3]) or pipDict(x, y, tGrid.TT[8]) or  pipDict(x, y, tGrid.TT[11]) or pipDict(x, y, tGrid.TT[1]) or pipDict(x, y, tGrid.TT[2]) or pipDict(x, y, tGrid.TT[9]) or  pipDict(x, y, tGrid.TT[10]):
        return True

def pipHorz(x, y):
    if pipDict(x, y, tGrid.TT[4]) or pipDict(x, y, tGrid.TT[7]) or pipDict(x, y, tGrid.TT[12]) or pipDict(x, y, tGrid.TT[15]) or pipDict(x, y, tGrid.TT[5]) or pipDict(x, y, tGrid.TT[6]) or pipDict(x, y, tGrid.TT[13]) or pipDict(x, y, tGrid.TT[14]):
        return True

def pipBot(x, y):
    if pipDict(x, y, tGrid.TT[0]) or pipDict(x, y, tGrid.TT[1]) or pipDict(x, y, tGrid.TT[2]) or pipDict(x, y, tGrid.TT[3]):
        return True

def pipRight(x, y):
    if pipDict(x, y, tGrid.TT[4]) or pipDict(x, y, tGrid.TT[5]) or pipDict(x, y, tGrid.TT[6]) or pipDict(x, y, tGrid.TT[7]):
        return True

def pipTop(x, y):
    if pipDict(x, y, tGrid.TT[8]) or pipDict(x, y, tGrid.TT[9]) or pipDict(x, y, tGrid.TT[10]) or pipDict(x, y, tGrid.TT[11]):
        return True

def pipLeft(x, y):
    if pipDict(x, y, tGrid.TT[12]) or pipDict(x, y, tGrid.TT[13]) or pipDict(x, y, tGrid.TT[14]) or pipDict(x, y, tGrid.TT[15]):
        return True
        
def printInfo():
    print ''
    print "Pad Size:", TPAD_H
    print "Row:", row, "\b, Col:", col
    print "Screen Dim - X:", SCR_W, "\b, Y:", SCR_H
    print "Board Dim - X:", boardW, "\b, Y:", boardH
    print "Pad Pitch - X:", tPadPx, "\b, Y:", tPadPy
    print 'Packed:', PACKED
    print ''
        
def inGrid(grid, TPs):
    validPts = []
    for i in range(len(TPs)):    
        if pipDict(TPs[i-1]['x'], TPs[i-1]['y'], grid):
            validPts.append(TPs[i-1])
    return validPts

def sortIntoGrids(grids, TPs):
    sorted = []
    
    for i in range(len(grids)):
        sorted.append(inGrid(grids[i], TPs))
        
    return sorted
                
def gridRouteAccum(TPs):
    list = []
    
    for i in range(len(TPs)):
        #print 'i:', i, 'len(TPs):', len(TPs)
        accum = {}
        if (i >= 0 and i <= 3) or (i >= 8 and i <= 11):
            for tp in TPs[i]:
                if tp['x'] not in accum:
                    accum[tp['x']] = []
                accum[tp['x']].append(tp['y'])
        elif (i >= 4 and i <= 7) or (i >= 12 and i <= 15):
            for tp in TPs[i]:
                if tp['y'] not in accum:
                    accum[tp['y']] = []
                accum[tp['y']].append(tp['x'])
        else:
            print 'shouldnt be here gridRouteAccum'
        list.append(accum)
    
    return list

def sideRouteAccum(touchPts):
    accum = {}
    
    for ptNum, pt in enumerate(touchPts):
        if pt['y'] not in accum:
            accum[pt['y']] = []
        accum[pt['y']].append(pt['x'])
        
    return accum
    
def padCalc(startLoc, pad, type, pitch, tPadMaxDim, padOffset, posOffset, padTotal):
    padList = []
    padList.append(startLoc)
    
    if type == 'calt':
        altCount = 1
        if padTotal%2 == 0: #even
            inTotal = padTotal/2
            outTotal = padTotal/2
        else: #odd
            inTotal = (padTotal/2) + 1
            outTotal = padTotal/2
        
        inTotal += padOffset
        outTotal -= padOffset
        
        for i in range(padTotal):
            if i%2==0: #even
                next = startLoc + altCount*pitch
            else: #odd
                next = startLoc - altCount*pitch
                altCount += 1
            padList.append(next)        
        
    elif type == 'cout':
        
        if padTotal%2 == 0: #even
            inTotal = padTotal/2
            outTotal = padTotal/2
        else: #odd
            inTotal = (padTotal/2) + 1
            outTotal = padTotal/2
            
        inTotal += padOffset
        outTotal -= padOffset
        
        for i in range(inTotal):
            next = startLoc + (tPadMaxDim/2 + (i+1)*pitch)
            padList.append(next)
            
        for i in range(outTotal):
            next = startLoc - (tPadMaxDim/2 + (i+1)*pitch)
            padList.append(next)
        
    elif type == 'cin':
        
        if padTotal%2 == 0: #even
            inTotal = padTotal/2
            outTotal = padTotal/2
        else: #odd
            inTotal = padTotal/2
            outTotal = (padTotal/2) + 1
            
        inTotal -= padOffset
        outTotal += padOffset
        
        for i in range(outTotal):
            next = startLoc - (tPadMaxDim/2 + (i+1)*pitch)
            padList.append(next)
        
        for i in range(inTotal):
            next = startLoc + (tPadMaxDim/2 + (i+1)*pitch)
            padList.append(next)
        
    elif type == 'in':
        
        for i in range(padTotal-padOffset):
            next = startLoc + (tPadMaxDim/2 + (i+1)*pitch)
            padList.append(next)
        if padOffset > 0:
            for i in range(padOffset):
                next = startLoc - (tPadMaxDim/2 + (i+1)*pitch)
                padList.append(next)
            
    elif type == 'out':
        
        for i in range(padTotal-padOffset):
            next = startLoc - (tPadMaxDim/2 + (i+1)*pitch)
            padList.append(next)
        if padOffset > 0:
            for i in range(padOffset):
                next = startLoc + (tPadMaxDim/2 + (i+1)*pitch)
                padList.append(next)
        
    else:
        print 'else case in padCalc'

    return padList[pad]
    
def padCalc2(startLoc, pad, type, pitch, tPadMaxDim, padTotal, above, below, first):
    padList = []
    padList.append(startLoc)
    
    if type == 'side':
        if (above+below) == padTotal:
            if first == 'above':
                for i in range(above):
                    next = startLoc + (tPadMaxDim/2 + (i+1)*pitch)
                    padList.append(next)
                for i in range(below):
                    next = startLoc - (tPadMaxDim/2 + (i+1)*pitch)
                    padList.append(next)
            elif first == 'below':
                for i in range(below):
                    next = startLoc - (tPadMaxDim/2 + (i+1)*pitch)
                    padList.append(next)
                for i in range(above):
                    next = startLoc + (tPadMaxDim/2 + (i+1)*pitch)
                    padList.append(next)
            else:
                print 'else case padCalc - side - first'
        else:
            print 'else case padCalc - side - padTotal'
            
            
    elif type == 'center':
        pass
        
    else:
        print 'else case pad calc - type'
    
    return padList[pad]

def matingPosSide(accumPts, pitch):
    ptPairs = []
    #{'tx': tx, 'ty': ty, 'mx': mx, 'my': my}
    for yValue in accumPts:
        padTotal = len(accumPts[yValue])
        for depth, xValue in enumerate(accumPts[yValue]):
            tx = xValue
            ty = yValue
            mx = -traceExtW/2
            my = padCalc(startLoc=yValue, pad=depth, type='calt', pitch=pitch, tPadMaxDim=TPAD_W, padOffset=0, posOffset=0, padTotal=padTotal)
            
            ptPairs.append({'tx': tx, 'ty': ty, 'mx': mx, 'my': my})
        
    return ptPairs
    
def matingPosGrid(accumPts, pitch, tPadMaxDim): 
    matingPts = []
    gridPts = []
    
    for gridNum, grid in enumerate(accumPts):
        gridPts = []
        
        for location in grid:
            padTotal = len(grid[location])
            
            if gridNum >= 0 and gridNum <= 3:
                for depth, pad in enumerate(grid[location]):
                    tx = location
                    ty = pad
                    mx = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                    my = -traceExtH/2
                    gridPts.append({'tx': tx, 'ty': ty, 'mx': mx, 'my': my})
            elif gridNum >= 4 and gridNum <= 7:
                for depth, pad in enumerate(grid[location][::-1]):
                    tx = pad
                    ty = location
                    mx = traceExtW/2
                    my = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                    gridPts.append({'tx': tx, 'ty': ty, 'mx': mx, 'my': my})
            elif gridNum >= 8 and gridNum <= 11:
                for depth, pad in enumerate(grid[location][::-1]):
                    tx = location
                    ty = pad
                    mx = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                    my = traceExtH/2
                    gridPts.append({'tx': tx, 'ty': ty, 'mx': mx, 'my': my})
            elif gridNum >= 12 and gridNum <= 15:
                for depth, pad in enumerate(grid[location]):
                    tx = pad
                    ty = location
                    mx = -traceExtW/2
                    my = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                    gridPts.append({'tx': tx, 'ty': ty, 'mx': mx, 'my': my})
            else:
                print 'Outside of gridNum bounds'
                
        matingPts.append(gridPts)
        
    return matingPts

def drawSide(allPtPairs, TPAD_W, TPAD_H, TRACE_W):
    padLayer = stPARA.LAYER_TPAD
    traceLayer = stPARA.LAYER_TRACE_TOP
    text_size = 0.8
    
    sortedPairs = sorted(allPtPairs, key=itemgetter('ty'))
    
    for num, pair in enumerate(sortedPairs):
        
        layer(padLayer)
        if TPAD_SHAPE == 'square':
            drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
        elif TPAD_SHAPE == 'circle':
            circlePoly(pair['tx'], pair['ty'], TPAD_W/2)
        elif TPAD_SHAPE == 'diamond':
            drawDiamond(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
        #drawCirclePoly(pair['tx'], pair['ty'], 4, 0.01)
        #if PACKED == False:
        via_noNet(pair['tx'], pair['ty'], VIA_DRILL_SIZE, VIA_UNIT, 0, 'round', 1, 16)
        
        if TOP_PAD_ENABLED:
            layer(TRACE_BOT_LAYER)
            if TOP_PAD_SHAPE == 'square':
                drawPolygon(pair['tx'], pair['ty'], TOP_PAD_SIZE, TOP_PAD_SIZE)
            elif TOP_PAD_SHAPE == 'circle':
                circlePoly(pair['tx'], pair['ty'], TOP_PAD_SIZE/2)
            elif TOP_PAD_SHAPE == 'diamond':
                drawDiamond(pair['tx'], pair['ty'], TOP_PAD_SIZE, TOP_PAD_SIZE)
                
        if TRACES_ENABLED:
            layer(traceLayer)
            setWireBend(1)
            wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
            
        if SWITCHES_ENABLED:
            lib = 'soft_touch.lbr'
            addPkg(RELAY_PKG, lib, RELAY_ANGLE, float(pair['tx'])+float(RELAY_XOFF), float(pair['ty'])+float(RELAY_YOFF))
            layer(TRACE_TOP_LAYER)
            setWireBend(2)
            wire(pair['tx'], pair['ty'], float(float(pair['tx'])+float(RELAY_XOFF)), float(float(pair['ty'])+float(RELAY_YOFF)), TRACE_W)
                    
        if TPAD_LABEL_ENABLED:
            text(str(num), pair['tx']-0.8, pair['ty']+(TOP_PAD_SIZE/2), text_size, stPARA.LABEL_TPAD_LABEL)
        
def drawGrid(allPtPairs, TPAD_W, TPAD_H, TRACE_W):
    
    mult = 0.45
    padLayer = stPARA.LAYER_TPAD
    traceLayer = stPARA.LAYER_TRACE_TOP
    counter = 0
    text_size = 0.8
    
    for gridIndex, grid in enumerate(allPtPairs):
        
        if gridIndex >= 0 and gridIndex <= 3:
            
            sortedGrid = sorted(grid, key=itemgetter('tx'))
            
            for pair in sortedGrid:
                
                layer(padLayer)
                if TPAD_SHAPE == 'square':
                    drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                elif TPAD_SHAPE == 'circle':
                    circlePoly(pair['tx'], pair['ty'], TPAD_W/2)
                elif TPAD_SHAPE == 'diamond':
                    drawDiamond(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                #if PACKED == False:
                via_noNet(pair['tx'], pair['ty'], VIA_DRILL_SIZE, VIA_UNIT, 0, 'round', 1, 16)
                if TPAD_LABEL_ENABLED:
                    text(str(counter), pair['tx']+text_size/2, pair['ty']+0.3, text_size, TPAD_LABEL_LAYER, 'R90')
                    
                if TOP_PAD_ENABLED:
                    layer(TRACE_BOT_LAYER)
                    if TOP_PAD_SHAPE == 'square':
                        drawPolygon(pair['tx'], pair['ty'], TOP_PAD_SIZE, TOP_PAD_SIZE)
                    elif TOP_PAD_SHAPE == 'circle':
                        circlePoly(pair['tx'], pair['ty'], TOP_PAD_SIZE/2)
                    elif TOP_PAD_SHAPE == 'diamond':
                        drawDiamond(pair['tx'], pair['ty'], TOP_PAD_SIZE, TOP_PAD_SIZE)
                    
                if TRACES_ENABLED:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
                
                if SWITCHES_ENABLED:
                    lib = 'soft_touch.lbr'
                    addPkg(RELAY_PKG, lib, RELAY_ANGLE, float(pair['tx'])+float(RELAY_XOFF), float(pair['ty'])+float(RELAY_YOFF))
                    
                counter=counter+1
                if MULTIPLE_LAYERS:
                    if counter%2:
                        traceLayer = traceLayerAlternator(traceLayer)
                    
        
        elif gridIndex >= 4 and gridIndex <= 7:
            
            sortedGrid = sorted(grid, key=itemgetter('ty'))
            
            for pair in sortedGrid:
                                
                layer(padLayer)
                drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                #if PACKED == False:
                via_noNet(pair['tx'], pair['ty'], VIA_DRILL_SIZE, VIA_UNIT, 0, 'round', 1, 16)
                if TPAD_LABEL_ENABLED:
                    text(str(counter), pair['tx']-0.3, pair['ty']+text_size/2, text_size, TPAD_LABEL_LAYER, 'R180')
                    
                if TOP_PAD_ENABLED:
                    layer(TRACE_BOT_LAYER)
                    if TOP_PAD_SHAPE == 'square':
                        drawPolygon(pair['tx'], pair['ty'], TOP_PAD_SIZE, TOP_PAD_SIZE)
                    elif TOP_PAD_SHAPE == 'circle':
                        circlePoly(pair['tx'], pair['ty'], TOP_PAD_SIZE/2)
                    elif TOP_PAD_SHAPE == 'diamond':
                        drawDiamond(pair['tx'], pair['ty'], TOP_PAD_SIZE, TOP_PAD_SIZE)
                    
                if TRACES_ENABLED:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
                    
                if SWITCHES_ENABLED:
                    lib = 'soft_touch.lbr'
                    addPkg(RELAY_PKG, lib, RELAY_ANGLE, float(pair['tx'])+float(RELAY_XOFF), float(pair['ty'])+float(RELAY_YOFF))
                    
                counter=counter+1
                if MULTIPLE_LAYERS:
                    if counter%2:
                        traceLayer = traceLayerAlternator(traceLayer)
        
        elif gridIndex >= 8 and gridIndex <= 11:
            
            sortedGrid = multikeysort(grid, ['tx', 'ty'])[::-1]
            
            for pair in sortedGrid:
                
                layer(padLayer)
                drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                #if PACKED == False:
                via_noNet(pair['tx'], pair['ty'], VIA_DRILL_SIZE, VIA_UNIT, 0, 'round', 1, 16)
                if TPAD_LABEL_ENABLED:
                    text(str(counter), pair['tx']-text_size/2, pair['ty']-0.3, text_size, TPAD_LABEL_LAYER, 'R270')
                    
                if TOP_PAD_ENABLED:
                    layer(TRACE_BOT_LAYER)
                    if TOP_PAD_SHAPE == 'square':
                        drawPolygon(pair['tx'], pair['ty'], TOP_PAD_SIZE, TOP_PAD_SIZE)
                    elif TOP_PAD_SHAPE == 'circle':
                        circlePoly(pair['tx'], pair['ty'], TOP_PAD_SIZE/2)
                    elif TOP_PAD_SHAPE == 'diamond':
                        drawDiamond(pair['tx'], pair['ty'], TOP_PAD_SIZE, TOP_PAD_SIZE)
                    
                if TRACES_ENABLED:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
                
                if SWITCHES_ENABLED:
                    lib = 'soft_touch.lbr'
                    addPkg(RELAY_PKG, lib, RELAY_ANGLE, float(pair['tx'])+float(RELAY_XOFF), float(pair['ty'])+float(RELAY_YOFF))
                
                counter=counter+1
                if MULTIPLE_LAYERS:
                    if counter%2:
                        traceLayer = traceLayerAlternator(traceLayer)
        
        elif gridIndex >= 12 and gridIndex <= 15:
            
            sortedGrid = multikeysort(grid, ['ty', '-tx'])[::-1]
            
            for pair in sortedGrid:
                   
                layer(padLayer)
                drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                #if PACKED == False:
                via_noNet(pair['tx'], pair['ty'], VIA_DRILL_SIZE, VIA_UNIT, 0, 'round', 1, 16)
                if TPAD_LABEL_ENABLED:
                    text(str(counter), pair['tx']+0.3, pair['ty']-text_size/2, text_size, TPAD_LABEL_LAYER)
                    
                if TOP_PAD_ENABLED:
                    layer(TRACE_BOT_LAYER)
                    if TOP_PAD_SHAPE == 'square':
                        drawPolygon(pair['tx'], pair['ty'], TOP_PAD_SIZE, TOP_PAD_SIZE)
                    elif TOP_PAD_SHAPE == 'circle':
                        circlePoly(pair['tx'], pair['ty'], TOP_PAD_SIZE/2)
                    elif TOP_PAD_SHAPE == 'diamond':
                        drawDiamond(pair['tx'], pair['ty'], TOP_PAD_SIZE, TOP_PAD_SIZE)
                    
                if TRACES_ENABLED:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
                    
                if SWITCHES_ENABLED:
                    lib = 'soft_touch.lbr'
                    addPkg(RELAY_PKG, lib, RELAY_ANGLE, float(pair['tx'])+float(RELAY_XOFF), float(pair['ty'])+float(RELAY_YOFF))
                    
                counter=counter+1
                if MULTIPLE_LAYERS:
                    if counter%2:
                        traceLayer = traceLayerAlternator(traceLayer)
        
        else:
            print 'gridIndex out of bounds when trying to draw'
            
    return counter

def packedSwitches():
    flip = -1
    for i in range(PACK_COL):
        for j in range(PACK_ROW):
            x = i*PACK_X+(PKG_W/2)-(PACK_X*PACK_COL)/2-RELAY_XOFF
            y = j*PACK_Y+(PKG_H/2)-(PACK_Y*PACK_ROW)/2-RELAY_YOFF
            #if flip == -1:
                #flip = 1
            #else:
                #flip = -1
            #layer(TRACE_TOP_LAYER)
            #setWireBend(2)
            #wire(pair['tx'], pair['ty'], float(float(pair['tx'])+float(RELAY_XOFF)), float(float(pair['ty'])+float(RELAY_YOFF)), TRACE_W)
            addPkg(RELAY_PKG, 'soft_touch.lbr', flip*RELAY_ANGLE, x, y)
            #via_noNet(x, y, 10, 0, 'round', 1, 16)
            

''' PATTERN PARAMETERS '''

parser = argparse.ArgumentParser()
parser.add_argument('cfg')
args = parser.parse_args()
CONFIGURATION_FILE_NAME = args.cfg

config = ConfigObj(file_error=True)
config.filename = CONFIGURATION_FILE_NAME
config.reload()

#config = ConfigParser.SafeConfigParser()
#config.read(CONFIGURATION_FILE_NAME)

SCRIPT_NAME = config['name']['scriptName']
SCRIPT_PATH = config['name']['scriptPath']

TPAD_W = float(config['pads']['size'])
TPAD_H = float(config['pads']['size'])
TPAD_POUR = str(config['pads']['fill'])
TPAD_POUR_SPACING = float(config['pads']['fillSpacing'])
TPAD_MAX_DIM = max(TPAD_W, TPAD_H)
TPAD_SPACING_DIM = float(config['pads']['padDimForSpacing'])
TPAD_SHAPE = str(config['pads']['shape'])
TPAD_LABEL_ENABLED = afunc.parseBooleanString(config['pads']['labels'])
VIA_UNIT = str(config['pads']['viaUnit'])
VIA_DRILL_SIZE = float(config['pads']['viaDrill'])

TOP_PAD_ENABLED = afunc.parseBooleanString(config['pads']['topPads'])
TOP_PAD_SHAPE = str(config['pads']['topPadShape'])
TOP_PAD_SIZE = float(config['pads']['topSize'])

TRACE_W = float(config['traces']['w'])
TRACE_P_MULTIPLIER = float(config['traces']['pitchMultiplier'])
TRACE_P = TRACE_P_MULTIPLIER*TRACE_W
MULTIPLE_LAYERS = afunc.parseBooleanString(config['traces']['multipleLayers'])

routing = config['traces']['routing']
setPitch = afunc.parseBooleanString(config['size']['setPitch'])
pitch = float(config['size']['pitch'])

MILLED = afunc.parseBooleanString(config['pads']['milled'])
MILLED_WIDTH = float(config['pads']['milledWidth'])

col = int(config['pads']['col'])
# row = 22

if setPitch:
    row = int(config['pads']['row'])
    SCR_W = pitch*(col-1) + TPAD_MAX_DIM
    SCR_H = pitch*(row-1) + TPAD_MAX_DIM
else:
    SCR_W = float(config['size']['w'])
    SCR_H = float(config['size']['h'])
    scrRatio = SCR_H/SCR_W
    row = int(round(scrRatio*col))

# col = int(round((1/scrRatio)*row))
tPadPx = float((SCR_W-TPAD_W)/(col-1))
tPadPy = float((SCR_H-TPAD_H)/(row-1))

SCR_B = float(config['size']['traceExtension'])

traceExtW = SCR_W + SCR_B
traceExtH = SCR_H + SCR_B
traceExtB = float(config['size']['routeExtension'])

routeW = traceExtW + traceExtB
routeH = traceExtH + traceExtB
routeB = float(config['size']['boardExtension'])

boardW = routeW + routeB
boardH = routeH + routeB

VI_OFFSET = float(config['traces']['VIoffset'])
vi = SCR_H/2 - SCR_W/2
triH = (0.6)*SCR_H/2
horzW = vi - TPAD_MAX_DIM/2
vertW = vi - 10

CONN_ENABLED = afunc.parseBooleanString(config['connectors']['enabled'])
CONN_PKG = config['connectors']['type']
CONN_PADPERROW = int(config['connectors'][str(CONN_PKG)]['padPerRow'])
CONN_ROWCOUNT = int(config['connectors'][str(CONN_PKG)]['rowCount'])
CONN_DIST = float(config['connectors'][str(CONN_PKG)]['dist'])
CONN_PITCH = float(config['connectors'][str(CONN_PKG)]['pitch'])
CONN_PADLENGTH = float(config['connectors'][str(CONN_PKG)]['padLength'])
CONN_INSIDECOUNT = int(config['connectors'][str(CONN_PKG)]['insideCount'])
CONN_TRACEWIDTH = float(config['connectors'][str(CONN_PKG)]['traceWidth'])
CONN_CLEARANCE = float(config['connectors'][str(CONN_PKG)]['clearance'])
CONN_XOFF = float(config['connectors'][str(CONN_PKG)]['xoffset'])
CONN_YOFF = float(config['connectors'][str(CONN_PKG)]['yoffset'])
CONN_ROTATION = float(config['connectors'][str(CONN_PKG)]['r'])

gridDisplay = afunc.parseBooleanString(config['traces']['gridDisplay'])
TRACES_ENABLED = afunc.parseBooleanString(config['traces']['enabled'])
SWITCHES_ENABLED = afunc.parseBooleanString(config['switches']['enabled'])

PACKED = afunc.parseBooleanString(config['switches']['packed'])
RELAY_PKG = config['switches']['type']
RELAY_ANGLE = float(config['switches'][str(RELAY_PKG)]['angle'])
RELAY_XOFF = float(config['switches'][str(RELAY_PKG)]['xoffset'])
RELAY_YOFF = float(config['switches'][str(RELAY_PKG)]['yoffset'])
PACK_X = float(config['switches'][str(RELAY_PKG)]['xpack'])
PACK_Y = float(config['switches'][str(RELAY_PKG)]['ypack'])
PKG_W = float(config['switches'][str(RELAY_PKG)]['pkgw'])
PKG_H = float(config['switches'][str(RELAY_PKG)]['pkgh'])
PACK_COL = int(config['switches'][str(RELAY_PKG)]['packcol'])
PACK_ROW = int(config['switches'][str(RELAY_PKG)]['packrow'])



class grid2Polys(object):
    def __init__(self):
        pass
    
    TT1_0 = {'x': -SCR_W/2, 'y': -SCR_H/2}
    TT1_1 = {'x': -SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    TT1_2 = {'x': -SCR_W/2 + TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    TT1_3 = {'x': -vertW, 'y': -triH}
    TT1_4 = {'x': -vertW, 'y': -SCR_H/2}
    TT1 = [TT1_0, TT1_1, TT1_2, TT1_3, TT1_4]

    TT2_0 = {'x': -vertW, 'y': -SCR_H/2}
    TT2_1 = {'x': -vertW, 'y': -horzW}
    TT2_2 = {'x': 0, 'y': -horzW}
    TT2_3 = {'x': 0, 'y': -SCR_H/2}
    TT2 = [TT2_0, TT2_1, TT2_2, TT2_3]

    TT3_0 = {'x': vertW, 'y': -SCR_H/2}
    TT3_1 = {'x': vertW, 'y': -horzW}
    TT3_2 = {'x': 0, 'y': -horzW}
    TT3_3 = {'x': 0, 'y': -SCR_H/2}
    TT3 = [TT3_0, TT3_1, TT3_2, TT3_3]

    TT4_0 = {'x': vertW, 'y': -SCR_H/2}
    TT4_1 = {'x': vertW, 'y': -triH}
    TT4_2 = {'x': SCR_W/2 - TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    TT4_3 = {'x': SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    TT4_4 = {'x': SCR_W/2, 'y': -SCR_H/2}
    TT4 = [TT4_0, TT4_1, TT4_2, TT4_3, TT4_4]

    TT5_0 = {'x': SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    TT5_1 = {'x': SCR_W/2 - TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    TT5_2 = {'x': vertW, 'y': -triH}
    TT5_3 = {'x': vertW, 'y': -horzW}
    TT5_4 = {'x': SCR_W/2, 'y': -horzW}
    TT5 = [TT5_0, TT5_1, TT5_2, TT5_3, TT5_4]

    TT6_0 = {'x': 0, 'y': -horzW}
    TT6_1 = {'x': 0, 'y': 0}
    TT6_2 = {'x': SCR_W/2, 'y': 0}
    TT6_3 = {'x': SCR_W/2, 'y': -horzW}
    TT6 = [TT6_0, TT6_1, TT6_2, TT6_3]

    TT7_0 = {'x': 0, 'y': 0}
    TT7_1 = {'x': 0, 'y': horzW}
    TT7_2 = {'x': SCR_W/2, 'y': horzW}
    TT7_3 = {'x': SCR_W/2, 'y': 0}
    TT7 = [TT7_0, TT7_1, TT7_2, TT7_3]

    TT8_0 = {'x': vertW, 'y': horzW}
    TT8_1 = {'x': vertW, 'y': triH}
    TT8_2 = {'x': SCR_W/2 - TPAD_W, 'y': SCR_H/2 - TPAD_H}
    TT8_3 = {'x': SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    TT8_4 = {'x': SCR_W/2, 'y': horzW}
    TT8 = [TT8_0, TT8_1, TT8_2, TT8_3, TT8_4]

    TT9_0 = {'x': vertW, 'y': triH}
    TT9_1 = {'x': vertW, 'y': SCR_H/2}
    TT9_2 = {'x': SCR_W/2, 'y': SCR_H/2}
    TT9_3 = {'x': SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    TT9_4 = {'x': SCR_W/2 - TPAD_W, 'y': SCR_H/2 - TPAD_H}
    TT9 = [TT9_0, TT9_1, TT9_2, TT9_3, TT9_4]

    TT10_0 = {'x': 0, 'y': SCR_H/2}
    TT10_1 = {'x': vertW, 'y': SCR_H/2}
    TT10_2 = {'x': vertW, 'y': horzW}
    TT10_3 = {'x': 0, 'y': horzW}
    TT10 = [TT10_0, TT10_1, TT10_2, TT10_3]
    
    TT11_0 = {'x': 0, 'y': horzW}
    TT11_1 = {'x': -vertW, 'y': horzW}
    TT11_2 = {'x': -vertW, 'y': SCR_H/2}
    TT11_3 = {'x': 0, 'y': SCR_H/2}
    TT11 = [TT11_0, TT11_1, TT11_2, TT11_3]

    TT12_0 = {'x': -vertW, 'y': triH}
    TT12_1 = {'x': -SCR_W/2 + TPAD_W, 'y': SCR_H/2 - TPAD_H}
    TT12_2 = {'x': -SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    TT12_3 = {'x': -SCR_W/2, 'y': SCR_H/2}
    TT12_4 = {'x': -vertW, 'y': SCR_H/2}
    TT12 = [TT12_0, TT12_1, TT12_2, TT12_3, TT12_4]

    TT13_0 = {'x': -vertW, 'y': horzW}
    TT13_1 = {'x': -SCR_W/2, 'y': horzW}
    TT13_2 = {'x': -SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    TT13_3 = {'x': -SCR_W/2 + TPAD_W, 'y': SCR_H/2 - TPAD_H}
    TT13_4 = {'x': -vertW, 'y': triH}
    TT13 = [TT13_0, TT13_1, TT13_2, TT13_3, TT13_4]

    TT14_0 = {'x': 0, 'y': 0}
    TT14_1 = {'x': -SCR_W/2, 'y': 0}
    TT14_2 = {'x': -SCR_W/2, 'y': horzW}
    TT14_3 = {'x': 0, 'y': horzW}
    TT14 = [TT14_0, TT14_1, TT14_2, TT14_3]
    
    TT15_0 = {'x': 0, 'y': -horzW}
    TT15_1 = {'x': -SCR_W/2, 'y': -horzW}
    TT15_2 = {'x': -SCR_W/2, 'y': 0}
    TT15_3 = {'x': 0, 'y': 0}
    TT15 = [TT15_0, TT15_1, TT15_2, TT15_3]

    TT16_0 = {'x': -SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    TT16_1 = {'x': -SCR_W/2, 'y': -horzW}
    TT16_2 = {'x': -vertW, 'y': -horzW}
    TT16_3 = {'x': -vertW, 'y': -triH}
    TT16_4 = {'x': -SCR_W/2 + TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    TT16 = [TT16_0, TT16_1, TT16_2, TT16_3, TT16_4]

    TT = [TT1, TT2, TT3, TT4, TT5, TT6, TT7, TT8, TT9, TT10, TT11, TT12, TT13, TT14, TT15, TT16]

tGrid = grid2Polys()
    
''' CREATE EAGLE SCRIPT '''

out = afunc.openFile(SCRIPT_NAME)

setVectorFont()
clearBoard()
createAllCustomLayers()
drawAllBorders()

setPadPour(TPAD_POUR, TPAD_POUR_SPACING)

drawBoard(routing)

if PACKED:
    packedSwitches()

if CONN_ENABLED:
    addPkg(CONN_PKG, 'soft_touch_lbr', CONN_ROTATION, CONN_XOFF, CONN_YOFF)
    fanout(padPerRow=CONN_PADPERROW,
        rowCount=CONN_ROWCOUNT,
        dist=CONN_DIST,
        pitch=CONN_PITCH,
        padLength=CONN_PADLENGTH,
        insideCount=CONN_INSIDECOUNT,
        traceWidth=CONN_TRACEWIDTH, #0.1016
        clearance=CONN_CLEARANCE,
        xo=CONN_XOFF,
        yo=CONN_YOFF,
        r=CONN_ROTATION,
        units='mm')
    
labelBoard()
window('FIT')
#hideTopLayer()
#hideBotLayer()
#hideTPADLayer()

#add('vssop_aqy221', 'vssop_aqy221', 'soft_touch_lbr')

afunc.closeFile(out)

printInfo()

''' RUN THE SCRIPT '''
runScript(DELAY, SCRIPT_PATH, SCRIPT_NAME)

#Delay needed to let Eagle process the script before it is deleted.
time.sleep(3)
#Remove generated Eagle script. These just add clutter. Just keep the .ini files.
afunc.removeFile(SCRIPT_PATH + SCRIPT_NAME)