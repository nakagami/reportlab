#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/lib/attrmap.py
__version__=''' $Id: attrmap.py 3660 2010-02-08 18:17:33Z damian $ '''
__doc__='''Framework for objects whose assignments are checked. Used by graphics.

We developed reportlab/graphics prior to Python 2 and metaclasses. For the
graphics, we wanted to be able to declare the attributes of a class, check
them on assignment, and convert from string arguments.  Examples of
attrmap-based objects can be found in reportlab/graphics/shapes.  It lets
us defined structures like the one below, which are seen more modern form in
Django models and other frameworks.

We'll probably replace this one day soon, hopefully with no impact on client
code.

class Rect(SolidShape):
    """Rectangle, possibly with rounded corners."""

    _attrMap = AttrMap(BASE=SolidShape,
        x = AttrMapValue(isNumber),
        y = AttrMapValue(isNumber),
        width = AttrMapValue(isNumber),
        height = AttrMapValue(isNumber),
        rx = AttrMapValue(isNumber),
        ry = AttrMapValue(isNumber),
        )


'''
try:
    from UserDict import UserDict
except ImportError:
    from collections import UserDict

from reportlab.lib.validators import isAnything, DerivedValue
from reportlab import rl_config

class CallableValue:
    '''a class to allow callable initial values'''
    def __init__(self,func,*args,**kw):
        #assert iscallable(func)
        self.func = func
        self.args = args
        self.kw = kw

    def __call__(self):
        return self.func(*self.args,**self.kw)

class AttrMapValue:
    '''Simple multi-value holder for attribute maps'''
    def __init__(self,validate=None,desc=None,initial=None, advancedUsage=0, **kw):
        self.validate = validate or isAnything
        self.desc = desc
        self._initial = initial
        self._advancedUsage = advancedUsage
        for k,v in kw.items():
            setattr(self,k,v)

    def __getattr__(self,name):
        #hack to allow callable initial values
        if name=='initial':
            if isinstance(self._initial,CallableValue): return self._initial()
            return self._initial
        elif name=='hidden':
            return 0
        raise AttributeError(name)

    def __repr__(self):
        return 'AttrMapValue(%s)' % ', '.join(['%s=%r' % i for i in self.__dict__.items()])

class AttrMap(UserDict):
    def __init__(self,BASE=None,**kw):
        data = {}
        if BASE:
            if isinstance(BASE,AttrMap):
                data = BASE.data                        #they used BASECLASS._attrMap
            else:
                if type(BASE) not in (type(()),type([])): BASE = (BASE,)
                for B in BASE:
                    if hasattr(B,'_attrMap'):
                        data.update(getattr(B._attrMap,'data',{}))
                    else:
                        raise ValueError('BASE=%s has wrong kind of value' % str(B))

        UserDict.__init__(self,data)
        self.data.update(kw)

    def update(self,kw):
        if isinstance(kw,AttrMap): kw = kw.data
        self.data.update(kw)

    def remove(self,unwanted):
        for k in unwanted:
            try:
                del self[k]
            except KeyError:
                pass

    def clone(self):
        c = AttrMap(BASE=self, **self.data)
        return c

def validateSetattr(obj,name,value):
    '''validate setattr(obj,name,value)'''
    if rl_config.shapeChecking:
        map = obj._attrMap
        if map and name[0]!= '_':
            #we always allow the inherited values; they cannot
            #be checked until draw time.
            if isinstance(value, DerivedValue):
                #let it through
                pass
            else:            
                try:
                    validate = map[name].validate
                    if not validate(value):
                        raise AttributeError("Illegal assignment of '%s' to '%s' in class %s" % (value, name, obj.__class__.__name__))
                except KeyError:
                    raise AttributeError("Illegal attribute '%s' in class %s" % (name, obj.__class__.__name__))
    obj.__dict__[name] = value
