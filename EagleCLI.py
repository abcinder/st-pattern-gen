''' EXPLICIT EAGLE FUNCTIONS '''

#def add(dev, lib, r='0', x=0, y=0):
    #return ('ADD ' + str(dev) + '@' + str(lib) + ' R' + str(r) + ' (' + str(x) + ' ' + str(y) + ')\r\n')

def add(name, pkg, lib, r='0', x=0, y=0):
    return ("ADD '" + str(name) + "' " + str(pkg) + "[@" + str(lib) + "]\r\n")
    click('left', x, y)

def addPkg(pkg, lib, r='0', x=0, y=0):
    return ('add '+str(pkg)+'@'+str(lib)+' R'+str(r)+' ('+str(x)+' '+str(y)+')\r\n')

def click(button, x=0, y=0):
    if button == 'left':
        return ('(' + str(x) + ' ' + str(y) + ')\r\n')   #left click
    elif button == 'right':
        return ('(>' + str(x) + ' ' + str(y) + ')\r\n')  #right click
    else:
        print 'error in click button input'

def close():
    return ('CLOSE\r\n')

def setSize(size):
    grid()
    return ('CHANGE SIZE ' + str(size) + '\r\n')

def change_pour(param='solid'):
    grid()
    return ('CHANGE POUR ' + str(param) + '\r\n')
    #CHANGE POUR SOLID | HATCH

def change_spacing(value):
    grid()
    return ('CHANGE SPACING ' + str(value) + '\r\n')

def setDrill(value, unit='mm'):
    grid(unit)
    return ('CHANGE DRILL ' + str(value) + '\r\n')
    grid()

def circlePoly(x, y, r, width=0.01):
    function = 'poly'
    net = 'ito'
    #poly gnd (P 10 0) +180 (P 10 180) +180 (P 10 0);

    return (function + ' ' + net + ' ' + str(width) + ' ' \
        '(' + str(x-(r)) + ' ' + str(y) + ')' + \
        '(' + str(x+(r)) + ' ' + str(y) + ')' + \
        ' +180 (' + str(x-(r)) + ' ' + str(y) + ')\r\n')

    return (function + ' ' + net + ' ' + str(width) + ' ' \
        '(' + str(x-(r)) + ' ' + str(y) + ')' + \
        '(' + str(x+(r)) + ' ' + str(y) + ')' + \
        ' -180 (' + str(x-(r)) + ' ' + str(y) + ')\r\n')

def circlePoly_v2(x, y, r, lineWidth=0.01):
    function = 'poly'
    net = 'ito'
    #poly gnd (P 10 0) +180 (P 10 180) +180 (P 10 0);

    return (function + ' ' + net + ' ' + str(width) + ' ' \
        '(' + str(x-(r)) + ' ' + str(y) + ')' + \
        '(' + str(x+(r)) + ' ' + str(y) + ')' + \
        ' +180 (' + str(x-(r)) + ' ' + str(y) + ')\r\n')

    return ()

def create_pad(w, h, r, name, x, y):
    return ('SMD ' + str(W) + ' ' + str(H) + ' ' + str(-1*r) + " '" + str(name) + "' (" + str(x) + ' ' + str(y) + ')\r\n')

def delete(x, y, button):
    if str(button).lower() == 'l':
        return ('DELETE\r\n')
        click('left', x, y)
    elif str(button).lower() == 'r':
        return ('DELETE\r\n')
        click('right', x, y)
    else:
        print 'INVALID DELETE "CLICK" PARAMETER'

def display(l):
    return ('DISPLAY ' + str(l) + '\r\n')

def edit(filename):
    return ('EDIT ' + str(filename) + '\r\n')

def grid(unit='mm', value=0.5, toggle='on'):
    return ('GRID ' + str(unit) + ' ' + str(value) + ' ' + str(toggle) + '\r\n')

def group(s):
    s = str(s)
    return ('GROUP (-'+s+' -'+s+') ('+s+' -'+s+') ('+s+' '+s+') (-'+s+' '+s+') (-'+s+' -'+s+')\r\n')

def layer(num, name=''):
    return ('LAYER ' + str(num) + ' ' + str(name) + '\r\n')

def move(e, x, y):
    return ('MOVE ' + str(e) + ' ('+str(x)+' '+str(y)+ ')\r\n')

def net(x1, y1, x2, y2, name='\b'):
    return ('NET ' + name + '('+str(x1)+' '+str(y1)+') ('+str(x2)+' '+str(y2)+')\r\n')

def openLibrary(lib):
    return ('OPEN ' + str(lib) + '\r\n')

def remove(filename):
    return ('REMOVE ' + str(filename) + '\r\n')

def removeDevice(dev):
    return ('REMOVE ' + str(dev) + '.dev\r\n')

def removePackage(pac):
    return ('REMOVE ' + str(pkg) + '.pac\r\n')

def removeSymbol(sym):
    return ('REMOVE ' + str(sym) + '.sym\r\n')

def rotate(e, r): #can also use to mirror, e.g. angle='MR90'
    return ('ROTATE ' + str(r) + ' ' + str(e) + '\r\n')

def route(x1, y1, x2, y2):
    return ('ROUTE ('+str(x1)+' '+str(y1)+') ('+str(x2)+' '+str(y2)+')\r\n')

def script(scr):
    return ('SCRIPT ' + str(scr) + '.scr\r\n')

def set(parameter, value):
    return ('SET ' + str(parameter) + ' ' + str(value) + '\r\n')

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
    return ('SIGNAL ' + net + ' ' + part1 + ' ' + pin1 + ' ' + part2 + ' ' + pin2 + '\r\n')

def text(string, x, y, size=1, layerNum=21, orientation=''):
    layer(layerNum) #tDocu
    setVectorFont()
    grid()
    setSize(size)
    return ('TEXT ' + str(string) + ' ' + str(orientation) + '\r\n')
    click('left', x, y)

def update(library):
    return ('UPDATE ' + str(library) + '\r\n')

def via_noNet(x, y, drill=10, unit= 'mil', diameter='0', shape='round', layer1=1, layer2=16):
    setDrill(drill, unit)
    return ('VIA ' + str(diameter) + ' ' + str(shape) + ' ' + str(layer1) + '-' + str(layer2) + '\r\n')
    click('left', x, y)
    grid()

def window(zoom):
    return ('WINDOW ' + str(zoom) + '\r\n')

def wire(x1, y1, x2, y2, width=0.1):
    return ('WIRE ' + str(width) +
                ' (' + str(x1) + ' ' + str(y1) + ')'+
                ' (' + str(x2) + ' ' + str(y2) + ')'+ '\r\n')

def write(): #aka SAVE
    return ('WRITE\r\n')