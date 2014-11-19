import pygtk
pygtk.require('2.0')
import time
import math
import re
import gtk
import wnck
from pykeyboard import PyKeyboard
from pymouse import PyMouse
import ConfigParser
import argparse
from operator import itemgetter
from fractions import gcd

DELAY = 0.5

''' VARIOUS FUNCTIONS '''

def parseBooleanString(string):
    return string[0].upper() == 'T'

def multikeysort(items, columns):
    from operator import itemgetter
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

def printList(list):
    for num, item in enumerate(list):
        print num, ' ', item
        
def runScript(delay, SCRIPT_NAME):
    screen = wnck.screen_get_default()

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
    m.click(x/2, y/2, 1)
    
    #KEYBOARD INPUT
    k = PyKeyboard()
    
    #BRING UP ALT-FILE MENU
    k.press_key(k.alt_key)
    k.type_string('f')
    k.release_key(k.alt_key)
    
    #PRESS T TO RUN SCRIPT FROM ALT-FILE MENU
    k.type_string('t')
    
    time.sleep(delay)
    
    #TYPE IN SCRIPT NAME TO DIALOG BOX
    k.type_string('/home/anton/Documents/st/' + SCRIPT_NAME)
    
    time.sleep(delay)
    
    k.tap_key(k.enter_key)
    
''' FILE I/O '''

def openFile(name):
    name = str(name)
    file = open(name, 'wb')
    print "Name of the file: ", file.name
    OddRow = True
    
    return file

def closeFile(file):
    file.close()
    print "Closed or not : ", file.closed


''' EXPLICIT EAGLE FUNCTIONS '''

def add(dev, lib, r='0', x=0, y=0):
    out.write('ADD ' + str(dev) + '@' + str(lib) + ' R' + str(r) + ' (' + str(x) + ' ' + str(y) + ')\r\n')
    
def click(button, x=0, y=0):
    if button == 'left':
        out.write('(' + str(x) + ' ' + str(y) + ')\r\n')   #left click
    elif button == 'right':
        out.write('(>' + str(x) + ' ' + str(y) + ')\r\n')  #right click
    else:
        print 'error in click button input'
    
def close():
    out.write('CLOSE\r\n')
    
def change_text_size(size):
    grid()
    out.write('CHANGE SIZE ' + str(size) + '\r\n')
    
def change_pour(param='solid'):
    grid()
    out.write('CHANGE POUR ' + str(param) + '\r\n')
    #CHANGE POUR SOLID | HATCH
    
def change_spacing(value):
    grid()
    out.write('CHANGE SPACING ' + str(value) + '\r\n')
    
def change_drill(value, unit):
    grid(unit)
    out.write('CHANGE DRILL ' + str(value) + '\r\n')
    grid()
    
def circlePoly(x, y, r, width=0.01):
    function = 'poly'
    net = 'ito'
    #poly gnd (P 10 0) +180 (P 10 180) +180 (P 10 0);
    
    out.write(function + ' ' + net + ' ' + str(width) + ' ' \
        '(' + str(x-(r/2)) + ' ' + str(y) + ')' + \
        '(' + str(x+(r/2)) + ' ' + str(y) + ')' + \
        ' +180 (' + str(x-(r/2)) + ' ' + str(y) + ')\r\n')

    out.write(function + ' ' + net + ' ' + str(width) + ' ' \
        '(' + str(x-(r/2)) + ' ' + str(y) + ')' + \
        '(' + str(x+(r/2)) + ' ' + str(y) + ')' + \
        ' -180 (' + str(x-(r/2)) + ' ' + str(y) + ')\r\n')
        
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
    set_vector_font()
    grid()
    change_text_size(size)
    out.write('TEXT ' + str(string) + ' ' + str(orientation) + '\r\n')
    click('left', x, y)
    
def update(library):
    out.write('UPDATE ' + str(library) + '\r\n')

def via_noNet(x, y, drill=8, diameter='0.5', shape='round', layer1=1, layer2=16):
    change_drill(drill, 'mil')
    out.write('VIA ' + str(diameter) + ' ' + str(shape) + ' ' + str(layer1) + '-' + str(layer2) + '\r\n')
    click('left', x, y)
    grid()
    
def window(zoom):
    out.write('WINDOW ' + str(zoom) + '\r\n')
    
def wire(x1, y1, x2, y2, width=0.1):
    out.write('WIRE ' + str(width) + " (" + str(x1) + ' ' + str(y1) + ') (' + str(x2) + ' ' + str(y2) +')'+"\r\n")

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
    
def change_tpad_pour(pour, spacing='1'):
    change_pour(pour)
    if str(pour) == 'hatch':
        change_spacing(spacing)
    
def clear_drawing(size):
    grid(unit='mm', value=0.5, toggle='on')
    display('ALL')
    group(size)
    delete(0,0,'r')  

def clear_schematic():
    switchToSchematic()
    clear_drawing(2000)
    
def clearBoard():
    switchToBoard()
    clear_drawing(2000)
    
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

def setMPadDim(w, h):
    openLibrary('ito')
    edit('ito_mpad.pac')
    changeSMD(w, h)
    write()
    close()
    
def setTPadDim(w, h):
    openLibrary('ito')
    edit('ito_tpad.pac')
    changeSMD(w, h)
    write()
    close()
    
def set_vector_font(setting='on'):
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

def label_tpad(num):
    pass

def create_all_layers():
    layer(TRACE_TOP_LAYER, 'TRACETOP')
    layer(TRACE_MID_LAYER, 'TRACEMID')
    layer(TRACE_BOT_LAYER, 'TRACEBOT')
    layer(TPAD_LAYER, 'TPAD')
    layer(TPAD_LABEL_LAYER, 'TPADLABEL')
    layer(GRID_TOP_LAYER, 'TOPGRID')
    layer(GRID_BOT_LAYER, 'BOTGRID')

def drawBorder(w, h, layer=20, width=0.1):
    setWireBendStraight()
    wireBoxWH(w, h, layer, width=0.1)

def drawPadsDictList(list, w=5, h=5):
    grid()
    for item in list:
        drawPolygon(item['x'], item['y'], w, h)

def drawAllGrids():
    for item in tGrid.BT:
        drawPolygonDict(item, GRID_BOT_LAYER)  

    for item in tGrid.TT:
        drawPolygonDict(item, GRID_TOP_LAYER)

def drawTouchPads():
    layer(TPAD_LAYER)
    for item in tPts_t:
        drawPadsDictList(item, TPAD_W, TPAD_H)

    layer(tPadBotLayer)
    for item in tPts_b:
        drawPadsDictList(item, TPAD_W, TPAD_H)

def hideTopLayer():
    display(-TPAD_LAYER)
    display(-mPadTopLayer)
    display(-TRACE_TOP_LAYER)
    display(-GRID_TOP_LAYER)
    
def hideBotLayer():
    display(-tPadBotLayer)
    display(-mPadBotLayer)
    display(-traceBotLayer)
    display(-GRID_BOT_LAYER)
    
def setPadDimensions(mw, mh, tw, th):
    setMPadDim(mw, mh)
    setTPadDim(tw, th)
    update('ito.lbr')

def showTopLayer():
    display(TPAD_LAYER)
    display(mPadTopLayer)
    display(TRACE_TOP_LAYER)
    display(GRID_TOP_LAYER)

def showBotLayer():
    display(tPadBotLayer)
    display(mPadBotLayer)
    display(traceBotLayer)
    display(GRID_BOT_LAYER)

def touchPos(col, row):
    posList = []
    
    for i in range(row):
        y = -SCR_H/2 + TPAD_H/2 + i*tPadPy
        for j in range(col):
            x = -SCR_W/2 + TPAD_W/2 + j*tPadPx
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
                
def mPtAccum(TPs):
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
            print 'shouldnt be here mPtAccum'
        list.append(accum)
    
    return list

def side_route_accum(touchPts):
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

def matingPos(accumPts, pitch):
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
    
def matingPosTop(accumPts, pitch, tPadMaxDim):
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

def matingPosBot(accumPts, pitch, tPadMaxDim):
    matingPts = []
    gridPts = []
    
    for gridNum, grid in enumerate(accumPts):
        gridPts = []
        
        for location in grid:
            padTotal = len(grid[location])
            
            for depth, pad in enumerate(grid[location][::-1]):
                ######### BOTTOM #########
                if gridNum == 0:
                    tx = location
                    ty = pad
                    mx = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                    my = -traceExtH/2
                elif gridNum == 1:
                    tx = location
                    ty = pad
                    mx = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                    my = -traceExtH/2
                elif gridNum == 2:
                    tx = location
                    ty = pad
                    mx = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                    my = -traceExtH/2
                elif gridNum == 3:
                    tx = location
                    ty = pad
                    mx = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                    my = -traceExtH/2
                ######### RIGHT #########
                elif gridNum == 4:
                    tx = pad
                    ty = location
                    mx = traceExtW/2
                    my = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=2, posOffset=0, padTotal=padTotal)
                elif gridNum == 5:
                    tx = pad
                    ty = location
                    mx = traceExtW/2
                    my = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                elif gridNum == 6:
                    tx = pad
                    ty = location
                    mx = traceExtW/2
                    my = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                elif gridNum == 7:
                    tx = pad
                    ty = location
                    mx = traceExtW/2
                    my = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=2, posOffset=0, padTotal=padTotal)
                ######### TOP #########
                elif gridNum == 8:
                    tx = location
                    ty = pad
                    mx = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=2, posOffset=0, padTotal=padTotal)
                    my = traceExtH/2
                elif gridNum == 9:
                    tx = location
                    ty = pad
                    mx = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                    my = traceExtH/2
                elif gridNum == 10:
                    tx = location
                    ty = pad
                    mx = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                    my = traceExtH/2
                elif gridNum == 11:
                    tx = location
                    ty = pad
                    mx = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=2, posOffset=0, padTotal=padTotal)
                    my = traceExtH/2
                ######### LEFT #########
                elif gridNum == 12:
                    tx = pad
                    ty = location
                    mx = -traceExtW/2
                    my = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=2, posOffset=0, padTotal=padTotal)
                elif gridNum == 13:
                    tx = pad
                    ty = location
                    mx = -traceExtW/2
                    my = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=0, posOffset=0, padTotal=padTotal)
                elif gridNum == 14:
                    tx = pad
                    ty = location
                    mx = -traceExtW/2
                    my = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=1, posOffset=0, padTotal=padTotal)
                elif gridNum == 15:
                    tx = pad
                    ty = location
                    mx = -traceExtW/2
                    my = padCalc(startLoc=location, pad=depth, type='calt', pitch=pitch, tPadMaxDim=tPadMaxDim, padOffset=2, posOffset=0, padTotal=padTotal)
                else:
                    print 'gridNum out of bounds in matingPos'
                    
                gridPts.append({'tx': tx, 'ty': ty, 'mx': mx, 'my': my})
                
        matingPts.append(gridPts)
    
    return matingPts

def drawPairs(allPtPairs, TPAD_W, TPAD_H, TRACE_W, traces=True):
    padLayer = TPAD_LAYER
    traceLayer = TRACE_TOP_LAYER
    
    sortedPairs = sorted(allPtPairs, key=itemgetter('ty'))
    
    for num, pair in enumerate(sortedPairs):
        
        layer(padLayer)
        drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
        #drawCirclePoly(pair['tx'], pair['ty'], 4, 0.01)
        via_noNet(pair['tx'], pair['ty'], 8, 0.5, 'round', 1, 16)
        
        if traces==True:
            layer(traceLayer)
            setWireBend(1)
            wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
        
        text(str(num), pair['tx']+0.5, pair['ty']+0.5, 0.5, TPAD_LABEL_LAYER) 
        
def drawTop(allPtPairs, TPAD_W, TPAD_H, TRACE_W, tPad=True, traces=True):
    
    mult = 0.45
    padLayer = TPAD_LAYER
    traceLayer = TRACE_BOT_LAYER
    counter = 0
    text_size = 0.8
    
    for gridIndex, grid in enumerate(allPtPairs):
        
        if gridIndex >= 0 and gridIndex <= 3:
            
            for pair in grid:
                
                if tPad == True:
                    layer(padLayer)
                    drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                    via_noNet(pair['tx'], pair['ty'], 8, 0.5, 'round', 1, 16)
                    text(str(counter), pair['tx']+text_size/2, pair['ty']+0.3, text_size, TPAD_LABEL_LAYER, 'R90') 
                
                if trace == True:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
                    
                counter=counter+1
        
        elif gridIndex >= 4 and gridIndex <= 7:
            
            sortedGrid = sorted(grid, key=itemgetter('ty'))
            
            for pair in sortedGrid:
                                
                if tPad == True:
                    layer(padLayer)
                    drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                    via_noNet(pair['tx'], pair['ty'], 8, 0.5, 'round', 1, 16)
                    text(str(counter), pair['tx']-0.3, pair['ty']+text_size/2, text_size, TPAD_LABEL_LAYER, 'R180') 
                    
                if trace == True:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
                
                counter=counter+1
        
        elif gridIndex >= 8 and gridIndex <= 11:
            
            sortedGrid = multikeysort(grid, ['tx', 'ty'])[::-1]
            
            for pair in sortedGrid:
                
                if tPad == True:
                    layer(padLayer)
                    drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                    via_noNet(pair['tx'], pair['ty'], 8, 0.5, 'round', 1, 16)
                    text(str(counter), pair['tx']-text_size/2, pair['ty']-0.3, text_size, TPAD_LABEL_LAYER, 'R270') 
                
                if trace == True:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
                
                counter=counter+1
        
        elif gridIndex >= 12 and gridIndex <= 15:
            
            sortedGrid = multikeysort(grid, ['ty', '-tx'])[::-1]
                        
            for pair in sortedGrid:
                
                if tPad == True:     
                    layer(padLayer)
                    drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                    via_noNet(pair['tx'], pair['ty'], 8, 0.5, 'round', 1, 16)
                    text(str(counter), pair['tx']+0.3, pair['ty']-text_size/2, text_size, TPAD_LABEL_LAYER) 
                
                if trace == True:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
                
                counter=counter+1
        
        else:
            print 'gridIndex out of bounds when trying to draw'
            
    return counter

def drawBot(allPtPairs, counter, TPAD_W, TPAD_H, TRACE_W, tPad=True, traces=True):
    
    mult = 0.45
    
    padLayer = TPAD_LAYER
    traceLayer = TRACE_BOT_LAYER
    
    for gridIndex, grid in enumerate(allPtPairs):

        for pair in grid:
            
            if gridIndex >= 0 and gridIndex <= 3:
                
                if tPad == True:
                    layer(padLayer)
                    drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                    via_noNet(pair['tx'], pair['ty'], 8, 0.5, 'round', 1, 16)
                    text(str(counter), pair['tx'], pair['ty'], 0.5, TPAD_LABEL_LAYER) 
                
                if trace == True:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
            
            elif gridIndex >= 4 and gridIndex <= 7:
                  
                if tPad == True:
                    layer(padLayer)
                    drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                    via_noNet(pair['tx'], pair['ty'], 8, 0.5, 'round', 1, 16)
                    text(str(counter), pair['tx'], pair['ty'], 0.5, TPAD_LABEL_LAYER) 
                    
                if trace == True:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
            
            elif gridIndex >= 8 and gridIndex <= 11:
                
                if tPad == True:    
                    layer(padLayer)
                    drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                    via_noNet(pair['tx'], pair['ty'], 8, 0.5, 'round', 1, 16)
                    text(str(counter), pair['tx'], pair['ty'], 0.5, TPAD_LABEL_LAYER) 
                
                if trace == True:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
            
            elif gridIndex >= 12 and gridIndex <= 15:
             
                if tPad == True:     
                    layer(padLayer)
                    drawPolygon(pair['tx'], pair['ty'], TPAD_W, TPAD_H)
                    via_noNet(pair['tx'], pair['ty'], 8, 0.5, 'round', 1, 16)
                    text(str(counter), pair['tx'], pair['ty'], 0.5, TPAD_LABEL_LAYER) 
                
                if trace == True:
                    layer(traceLayer)
                    setWireBend(1)
                    wire(pair['mx'], pair['my'], pair['tx'], pair['ty'], TRACE_W)
            
            else:
                print 'gridIndex out of bounds when trying to draw'
            counter=counter+1
                
''' EAGLE PARAMETERS '''

DIMENSION_LAYER = 20
TRACE_TOP_LAYER = 101
TRACE_MID_LAYER = 102
TRACE_BOT_LAYER = 115
TPAD_LAYER = 116
TPAD_LABEL_LAYER = 117
GRID_TOP_LAYER = 121
GRID_BOT_LAYER = 122

''' PATTERN PARAMETERS '''


parser = argparse.ArgumentParser()
parser.add_argument('cfg')
args = parser.parse_args()
CONFIGURATION_FILE_NAME = args.cfg

config = ConfigParser.SafeConfigParser()
config.read(CONFIGURATION_FILE_NAME)

SCRIPT_NAME = config.get('soft-touch-pattern-names', 'scriptName')

TPAD_W = float(config.get('touch-pads', 'touchPadW'))
TPAD_H = float(config.get('touch-pads', 'touchPadH'))
TPAD_POUR = str(config.get('touch-pads', 'fill'))
TPAD_POUR_SPACING = float(config.get('touch-pads', 'spacing'))

TRACE_W = float(config.get('traces', 'traceWidth'))
TRACE_P_MULTIPLIER = float(config.get('traces', 'tracePitchMultiplier'))
TRACE_P = TRACE_P_MULTIPLIER*TRACE_W

SCR_W = float(config.get('pattern-size', 'screenW'))
SCR_H = float(config.get('pattern-size', 'screenH'))
SCR_B = float(config.get('pattern-size', 'traceExtension'))

traceExtW = SCR_W + SCR_B
traceExtH = SCR_H + SCR_B
traceExtB = float(config.get('pattern-size', 'routeExtension'))

routeW = traceExtW + traceExtB
routeH = traceExtH + traceExtB
routeB = float(config.get('pattern-size', 'boardExtension'))

boardW = routeW + routeB
boardH = routeH + routeB

col = int(config.get('resolution', 'col'))
# row = 22
scrRatio = SCR_H/SCR_W
row = int(round(scrRatio*col))
# col = int(round((1/scrRatio)*row))
tPadPx = float((SCR_W-TPAD_W)/(col-1))
tPadPy = float((SCR_H-TPAD_H)/(row-1))

vi = SCR_H/2 - SCR_W/2
triH = (0.6)*SCR_H/2
rectW = vi - 3.5
rExtra = rectW + float(1)
mInsideW = rExtra + float(5)

class touchPolys(object):
    def __init__(self):
        pass
    
    TT1_0 = {'x': -SCR_W/2, 'y': -SCR_H/2}
    TT1_1 = {'x': -SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    TT1_2 = {'x': -SCR_W/2 + TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    TT1_3 = {'x': -rExtra, 'y': -triH}
    TT1_4 = {'x': -rExtra, 'y': -SCR_H/2}
    TT1 = [TT1_0, TT1_1, TT1_2, TT1_3, TT1_4]

    TT2_0 = {'x': -rExtra, 'y': -SCR_H/2}
    TT2_1 = {'x': -rExtra, 'y': -rExtra}
    TT2_2 = {'x': -rectW, 'y': -rectW}
    TT2_3 = {'x': 1, 'y': -rectW}
    TT2_4 = {'x': 1, 'y': -SCR_H/2}
    TT2 = [TT2_0, TT2_1, TT2_2, TT2_3, TT2_4]

    TT3_0 = {'x': rExtra, 'y': -SCR_H/2}
    TT3_1 = {'x': rExtra, 'y': -rExtra}
    TT3_2 = {'x': rectW, 'y': -rectW}
    TT3_3 = {'x': 1, 'y': -rectW}
    TT3_4 = {'x': 1, 'y': -SCR_H/2}
    TT3 = [TT3_0, TT3_1, TT3_2, TT3_3, TT3_4]

    TT4_0 = {'x': rExtra, 'y': -SCR_H/2}
    TT4_1 = {'x': rExtra, 'y': -triH}
    TT4_2 = {'x': SCR_W/2 - TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    TT4_3 = {'x': SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    TT4_4 = {'x': SCR_W/2, 'y': -SCR_H/2}
    TT4 = [TT4_0, TT4_1, TT4_2, TT4_3, TT4_4]

    TT5_0 = {'x': SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    TT5_1 = {'x': SCR_W/2 - TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    TT5_2 = {'x': rExtra, 'y': -triH}
    TT5_3 = {'x': rExtra, 'y': -rExtra}
    TT5_4 = {'x': SCR_W/2, 'y': -rExtra}
    TT5 = [TT5_0, TT5_1, TT5_2, TT5_3, TT5_4]

    TT6_0 = {'x': 1, 'y': -rectW}
    TT6_1 = {'x': 1, 'y': 1}
    TT6_2 = {'x': SCR_W/2, 'y': 1}
    TT6_3 = {'x': SCR_W/2, 'y': -rExtra}
    TT6_4 = {'x': rExtra, 'y': -rExtra}
    TT6_5 = {'x': rectW, 'y': -rectW}
    TT6 = [TT6_0, TT6_1, TT6_2, TT6_3, TT6_4, TT6_5]

    TT7_0 = {'x': 1, 'y': 1}
    TT7_1 = {'x': 1, 'y': rectW}
    TT7_2 = {'x': rectW, 'y': rectW}
    TT7_3 = {'x': rExtra, 'y': rExtra}
    TT7_4 = {'x': SCR_W/2, 'y': rExtra}
    TT7_5 = {'x': SCR_W/2, 'y': 1}
    TT7 = [TT7_0, TT7_1, TT7_2, TT7_3, TT7_4, TT7_5]

    TT8_0 = {'x': rExtra, 'y': rExtra}
    TT8_1 = {'x': rExtra, 'y': triH}
    TT8_2 = {'x': SCR_W/2 - TPAD_W, 'y': SCR_H/2 - TPAD_H}
    TT8_3 = {'x': SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    TT8_4 = {'x': SCR_W/2, 'y': rExtra}
    TT8 = [TT8_0, TT8_1, TT8_2, TT8_3, TT8_4]

    TT9_0 = {'x': rExtra, 'y': triH}
    TT9_1 = {'x': rExtra, 'y': SCR_H/2}
    TT9_2 = {'x': SCR_W/2, 'y': SCR_H/2}
    TT9_3 = {'x': SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    TT9_4 = {'x': SCR_W/2 - TPAD_W, 'y': SCR_H/2 - TPAD_H}
    TT9 = [TT9_0, TT9_1, TT9_2, TT9_3, TT9_4]

    TT10_0 = {'x': 0+1, 'y': rectW}
    TT10_1 = {'x': 0+1, 'y': SCR_H/2}
    TT10_2 = {'x': rExtra, 'y': SCR_H/2}
    TT10_3 = {'x': rExtra, 'y': rExtra}
    TT10_4 = {'x': rectW, 'y': rectW}
    TT10 = [TT10_0, TT10_1, TT10_2, TT10_3, TT10_4]

    TT11_0 = {'x': -rectW, 'y': rectW}
    TT11_1 = {'x': -rExtra, 'y': rExtra}
    TT11_2 = {'x': -rExtra, 'y': SCR_H/2}
    TT11_3 = {'x': 1, 'y': SCR_H/2}
    TT11_4 = {'x': 1, 'y': rectW}
    TT11 = [TT11_0, TT11_1, TT11_2, TT11_3, TT11_4]

    TT12_0 = {'x': -rExtra, 'y': triH}
    TT12_1 = {'x': -SCR_W/2 + TPAD_W, 'y': SCR_H/2 - TPAD_H}
    TT12_2 = {'x': -SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    TT12_3 = {'x': -SCR_W/2, 'y': SCR_H/2}
    TT12_4 = {'x': -rExtra, 'y': SCR_H/2}
    TT12 = [TT12_0, TT12_1, TT12_2, TT12_3, TT12_4]

    TT13_0 = {'x': -rExtra, 'y': rExtra}
    TT13_1 = {'x': -SCR_W/2, 'y': rExtra}
    TT13_2 = {'x': -SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    TT13_3 = {'x': -SCR_W/2 + TPAD_W, 'y': SCR_H/2 - TPAD_H}
    TT13_4 = {'x': -rExtra, 'y': triH}
    TT13 = [TT13_0, TT13_1, TT13_2, TT13_3, TT13_4]

    TT14_0 = {'x': 1, 'y': 1}
    TT14_1 = {'x': -SCR_W/2, 'y': 1}
    TT14_2 = {'x': -SCR_W/2, 'y': rExtra}
    TT14_3 = {'x': -rExtra, 'y': rExtra}
    TT14_4 = {'x': -rectW, 'y': rectW}
    TT14_5 = {'x': 1, 'y': rectW}
    TT14 = [TT14_0, TT14_1, TT14_2, TT14_3, TT14_4, TT14_5]

    TT15_0 = {'x': 1, 'y': -rectW}
    TT15_1 = {'x': -rectW, 'y': -rectW}
    TT15_2 = {'x': -rExtra, 'y': -rExtra}
    TT15_3 = {'x': -SCR_W/2, 'y': -rExtra}
    TT15_4 = {'x': -SCR_W/2, 'y': 1}
    TT15_5 = {'x': 1, 'y': 1}
    TT15 = [TT15_0, TT15_1, TT15_2, TT15_3, TT15_4, TT15_5]

    TT16_0 = {'x': -SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    TT16_1 = {'x': -SCR_W/2, 'y': -rExtra}
    TT16_2 = {'x': -rExtra, 'y': -rExtra}
    TT16_3 = {'x': -rExtra, 'y': -triH}
    TT16_4 = {'x': -SCR_W/2 + TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    TT16 = [TT16_0, TT16_1, TT16_2, TT16_3, TT16_4]

    TT = [TT1, TT2, TT3, TT4, TT5, TT6, TT7, TT8, TT9, TT10, TT11, TT12, TT13, TT14, TT15, TT16]
    
    BT1_0 = {'x': -SCR_W/2, 'y': -SCR_H/2}
    BT1_1 = {'x': -SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    BT1_2 = {'x': -SCR_W/2 + TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    BT1_3 = {'x': -rExtra, 'y': -triH}
    BT1_4 = {'x': -rExtra, 'y': -SCR_H/2}
    BT1 = [BT1_0, BT1_1, BT1_2, BT1_3, BT1_4]

    BT2_0 = {'x': -rExtra, 'y': -SCR_H/2}
    BT2_1 = {'x': -rExtra, 'y': -rExtra}
    BT2_2 = {'x': -rectW, 'y': -rectW}
    BT2_3 = {'x': 1, 'y': -rectW}
    BT2_4 = {'x': 1, 'y': -SCR_H/2}
    BT2 = [BT2_0, BT2_1, BT2_2, BT2_3, BT2_4]

    BT3_0 = {'x': rExtra, 'y': -SCR_H/2}
    BT3_1 = {'x': rExtra, 'y': -rExtra}
    BT3_2 = {'x': rectW, 'y': -rectW}
    BT3_3 = {'x': 1, 'y': -rectW}
    BT3_4 = {'x': 1, 'y': -SCR_H/2}
    BT3 = [BT3_0, BT3_1, BT3_2, BT3_3, BT3_4]

    BT4_0 = {'x': rExtra, 'y': -SCR_H/2}
    BT4_1 = {'x': rExtra, 'y': -triH}
    BT4_2 = {'x': SCR_W/2 - TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    BT4_3 = {'x': SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    BT4_4 = {'x': SCR_W/2, 'y': -SCR_H/2}
    BT4 = [BT4_0, BT4_1, BT4_2, BT4_3, BT4_4]

    BT5_0 = {'x': SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    BT5_1 = {'x': SCR_W/2 - TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    BT5_2 = {'x': rExtra, 'y': -triH}
    BT5_3 = {'x': rExtra, 'y': -rExtra}
    BT5_4 = {'x': SCR_W/2, 'y': -rExtra}
    BT5 = [BT5_0, BT5_1, BT5_2, BT5_3, BT5_4]

    BT6_0 = {'x': 1, 'y': -rectW}
    BT6_1 = {'x': 1, 'y': 1}
    BT6_2 = {'x': SCR_W/2, 'y': 1}
    BT6_3 = {'x': SCR_W/2, 'y': -rExtra}
    BT6_4 = {'x': rExtra, 'y': -rExtra}
    BT6_5 = {'x': rectW, 'y': -rectW}
    BT6 = [BT6_0, BT6_1, BT6_2, BT6_3, BT6_4, BT6_5]

    BT7_0 = {'x': 1, 'y': 1}
    BT7_1 = {'x': 1, 'y': rectW}
    BT7_2 = {'x': rectW, 'y': rectW}
    BT7_3 = {'x': rExtra, 'y': rExtra}
    BT7_4 = {'x': SCR_W/2, 'y': rExtra}
    BT7_5 = {'x': SCR_W/2, 'y': 1}
    BT7 = [BT7_0, BT7_1, BT7_2, BT7_3, BT7_4, BT7_5]

    BT8_0 = {'x': rExtra, 'y': rExtra}
    BT8_1 = {'x': rExtra, 'y': triH}
    BT8_2 = {'x': SCR_W/2 - TPAD_W, 'y': SCR_H/2 - TPAD_H}
    BT8_3 = {'x': SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    BT8_4 = {'x': SCR_W/2, 'y': rExtra}
    BT8 = [BT8_0, BT8_1, BT8_2, BT8_3, BT8_4]

    BT9_0 = {'x': rExtra, 'y': triH}
    BT9_1 = {'x': rExtra, 'y': SCR_H/2}
    BT9_2 = {'x': SCR_W/2, 'y': SCR_H/2}
    BT9_3 = {'x': SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    BT9_4 = {'x': SCR_W/2 - TPAD_W, 'y': SCR_H/2 - TPAD_H}
    BT9 = [BT9_0, BT9_1, BT9_2, BT9_3, BT9_4]

    BT10_0 = {'x': 1, 'y': rectW}
    BT10_1 = {'x': 1, 'y': SCR_H/2}
    BT10_2 = {'x': rExtra, 'y': SCR_H/2}
    BT10_3 = {'x': rExtra, 'y': rExtra}
    BT10_4 = {'x': rectW, 'y': rectW}
    BT10 = [BT10_0, BT10_1, BT10_2, BT10_3, BT10_4]

    BT11_0 = {'x': -rectW, 'y': rectW}
    BT11_1 = {'x': -rExtra, 'y': rExtra}
    BT11_2 = {'x': -rExtra, 'y': SCR_H/2}
    BT11_3 = {'x': 1, 'y': SCR_H/2}
    BT11_4 = {'x': 1, 'y': rectW}
    BT11 = [BT11_0, BT11_1, BT11_2, BT11_3, BT11_4]

    BT12_0 = {'x': -rExtra, 'y': triH}
    BT12_1 = {'x': -SCR_W/2 + TPAD_W, 'y': SCR_H/2 - TPAD_H}
    BT12_2 = {'x': -SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    BT12_3 = {'x': -SCR_W/2, 'y': SCR_H/2}
    BT12_4 = {'x': -rExtra, 'y': SCR_H/2}
    BT12 = [BT12_0, BT12_1, BT12_2, BT12_3, BT12_4]

    BT13_0 = {'x': -rExtra, 'y': rExtra}
    BT13_1 = {'x': -SCR_W/2, 'y': rExtra}
    BT13_2 = {'x': -SCR_W/2, 'y': SCR_H/2 - TPAD_H}
    BT13_3 = {'x': -SCR_W/2 + TPAD_W, 'y': SCR_H/2 - TPAD_H}
    BT13_4 = {'x': -rExtra, 'y': triH}
    BT13 = [BT13_0, BT13_1, BT13_2, BT13_3, BT13_4]

    BT14_0 = {'x': 1, 'y': 1}
    BT14_1 = {'x': -SCR_W/2, 'y': 1}
    BT14_2 = {'x': -SCR_W/2, 'y': rExtra}
    BT14_3 = {'x': -rExtra, 'y': rExtra}
    BT14_4 = {'x': -rectW, 'y': rectW}
    BT14_5 = {'x': 1, 'y': rectW}
    BT14 = [BT14_0, BT14_1, BT14_2, BT14_3, BT14_4, BT14_5]

    BT15_0 = {'x': 1, 'y': -rectW}
    BT15_1 = {'x': -rectW, 'y': -rectW}
    BT15_2 = {'x': -rExtra, 'y': -rExtra}
    BT15_3 = {'x': -SCR_W/2, 'y': -rExtra}
    BT15_4 = {'x': -SCR_W/2, 'y': 1}
    BT15_5 = {'x': 1, 'y': 1}
    BT15 = [BT15_0, BT15_1, BT15_2, BT15_3, BT15_4, BT15_5]

    BT16_0 = {'x': -SCR_W/2, 'y': -SCR_H/2 + TPAD_H}
    BT16_1 = {'x': -SCR_W/2, 'y': -rExtra}
    BT16_2 = {'x': -rExtra, 'y': -rExtra}
    BT16_3 = {'x': -rExtra, 'y': -triH}
    BT16_4 = {'x': -SCR_W/2 + TPAD_W, 'y': -SCR_H/2 + TPAD_H}
    BT16 = [BT16_0, BT16_1, BT16_2, BT16_3, BT16_4]

    BT = [BT1, BT2, BT3, BT4, BT5, BT6, BT7, BT8, BT9, BT10, BT11, BT12, BT13, BT14, BT15, BT16]

    
''' CREATE EAGLE SCRIPT '''

out = openFile(SCRIPT_NAME)

#setPadDimensions(mPadL, mPadW, TPAD_W, TPAD_H)

set_vector_font()

clearBoard()
create_all_layers()
drawBorder(SCR_W, SCR_H) 
drawBorder(traceExtW, traceExtH)
drawBorder(routeW, routeH)
drawBorder(boardW, boardH)

tGrid = touchPolys()

change_tpad_pour(TPAD_POUR, TPAD_POUR_SPACING)

routing = config.get('pattern-routing', 'routing')
gridDisplay = parseBooleanString(config.get('pattern-routing', 'gridDisplay'))

tracesEnabled = parseBooleanString(config.get('traces', 'enabled'))

if routing == 'side':
    tPts = touchPos(col, row)
    tPt_accum = side_route_accum(tPts)
    allPairs = matingPos(tPt_accum, TRACE_P)
    drawPairs(allPairs, TPAD_W, TPAD_H, TRACE_W, traces=stracesEnabled)
elif routing == 'grids':
    if gridDisplay:
        drawAllGrids()
    else:
        display(-GRID_TOP_LAYER)
        display(-GRID_BOT_LAYER)
    
    tPts = touchPos(col, row)
    tPts = sortIntoGrids(tGrid.TT, tPts)
    tPts_accum = mPtAccum(tPts)
    pairs = matingPosTop(tPts_accum, TRACE_P, TPAD_W)
    
    drawTop(pairs, TPAD_W, TPAD_H, TRACE_W, tPad=True, traces=tracesEnabled)
    
    #tPts_t, tPts_b = touchPosEven(col, row)
    #tPts_t = sortIntoGrids(tGrid.TT, tPts_t)
    #tPts_accum_t = mPtAccum(tPts_t)
    #topPadPairs = matingPosTop(tPts_accum_t, TRACE_P, TPAD_W)
    #counter = drawTop(topPadPairs, TPAD_W, TPAD_H, TRACE_W, tPad=True, trace=True)

    #tPts_b = sortIntoGrids(tGrid.BT, tPts_b)
    #tPts_accum_b = mPtAccum(tPts_b)
    #botPadPairs = matingPosBot(tPts_accum_b, TRACE_P, TPAD_W)
    #drawBot(botPadPairs, counter, TPAD_W, TPAD_H, TRACE_W, tPad=True, trace=True)
else:
    print 'error in routing configuration file params'

title = config.get('soft-touch-pattern-names', 'title')
text(title, float(-boardW/2+0.5), float(boardH/2-1.5), 1)
pad_string = 'row: ' + str(row) + ', col: ' + str(col) + ', pad: ' + str(int(TPAD_H)) 
text(pad_string, float(-boardW/2+0.5), float(boardH/2-3), 1)
trace_string = 'width: ' + str(TRACE_W) + ', pitch: ' + str(TRACE_P)
text(trace_string, float(-boardW/2+0.5), float(boardH/2-4.5), 1)

#hideTopLayer()
#hideBotLayer()



window('FIT')
closeFile(out)


''' RUN THE SCRIPT '''
runScript(DELAY, SCRIPT_NAME)
