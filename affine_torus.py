#!$HOME/anaconda/bin/python
# -*- coding: utf-8 -*-
'''
Ripped from template.py 
- makes a spiral pattern for laser cutting
'''

import inkex       # Required
import simplestyle # will be needed here for styles support
import os          # here for alternative debug method only - so not usually required.
from math import cos,sin,pi, exp


__version__ = '0.1'

inkex.localize()




    
    
def line(npts=40,
	x0=0,
	y0=0,
	delta=.5,	
	 sgn=1):
        '''returns a list of points on a line (y = +/- x + c) starting at x0,y0'''
	
	return [ (x0 + delta*t, y0 + sgn*delta*t) for t in range(npts)]
	
def ff(v,
       ww=.25,
       ds=.4):
        '''covering map from R^2 ro punctured plane'''
	x,y = v
	r,u = exp(-ds*x), cos(pi*ww*y) + 1J*sin(pi*ww*y)
	return r*u
    
def mk_plugs(pts):
    
    '''returns a list of complex representing a plug type segment'''
    
    def fit_plug(ss):
	a,b = ss
	rot = complex(b-a)
	pts = [0,.45,.4 + .15*1J, .6 + .15*1J, .55, 1]
	return [rot*z + a for z in pts]
    
    segs = [fit_plug(end_pts) for end_pts in zip(pts,pts[1:]) ]
    tmp  = []
    for seg in segs:
	tmp.extend(seg)
	
    return tmp


def pts2curve(cplxs):
    '''makes a polyline path element from a list of complex
    '''
    def cplx2pt(z):
        return (z.real,z.imag)
    
    scale = 200
    data = [cplx2pt( scale*z ) for z in cplxs ] 
    pth = [ '%.2f, %.2f '%z for z in data]
    return 'M '+ ''.join(pth) 
        



class Myextension(inkex.Effect): # choose a better name
    
    def __init__(self):
        " define how the options are mapped from the inx file "
        inkex.Effect.__init__(self) # initialize the super class
        
        # Two ways to get debug info:
        # OR just use inkex.debug(string) instead...
        try:
            self.tty = open("/dev/tty", 'w')
        except:
            self.tty = open(os.devnull, 'w')  # '/dev/null' for POSIX, 'nul' for Windows.
            # print >>self.tty, "gears-dev " + __version__
            
        # list of parameters defined in the .inx file
        self.OptionParser.add_option("-t", "--num_lines",
                                     action="store", type="int",
                                     dest="depth", default=3,
                                     help="command line help")
        
        self.OptionParser.add_option("-x", "--num_petals",
                                     action="store", type="int",
                                     dest="num_petals", default=3,
                                     help="command line help")
        
        self.OptionParser.add_option("", "--shrink_ratio",
                                     action="store", type="float",
                                     dest="shrink_factor", default=3,
                                     help="command line help")

    
        
        #self.OptionParser.add_option("-r", "--mk_filled",
        #                             action="store", type="inkbool", 
        #                             dest="mk_filled", default=False,
        #                             help="command line help")
        #
                
        self.OptionParser.add_option("", "--mk_full",
                                     action="store", type="inkbool", 
                                     dest="mk_full", default=False,
                                     help="command line help")


        # here so we can have tabs - but we do not use it directly - else error
        self.OptionParser.add_option("", "--active-tab",
                                     action="store", type="string",
                                     dest="active_tab", default='title', # use a legitmate default
                                     help="Active tab.")
        
 
           
    def calc_unit_factor(self):
        """ return the scale factor for all dimension conversions.
            - The document units are always irrelevant as
              everything in inkscape is expected to be in 90dpi pixel units
        """
        # namedView = self.document.getroot().find(inkex.addNS('namedview', 'sodipodi'))
        # doc_units = self.getUnittouu(str(1.0) + namedView.get(inkex.addNS('document-units', 'inkscape')))
        unit_factor = self.getUnittouu(str(1.0) + self.options.units)
        return unit_factor


### -------------------------------------------------------------------
### Main function and is called when the extension is run.

    
    def effect(self):

        #set up path styles
        path_stroke = '#DD0000' # take color from tab3
        path_fill   = 'none'     # no fill - just a line
        path_stroke_width  = 1. # can also be in form '0.6mm'
        page_id = self.options.active_tab # sometimes wrong the very first time
        
  
        styles = [ { 'stroke':  path_stroke , 'fill': 'none', 'stroke-width': path_stroke_width },
                   { 'stroke': 'none',  'fill': '#FFFF00', 'stroke-width': 0 }]
        
        styles = [simplestyle.formatStyle(x) for x in styles]

        

        # This finds center of current view in inkscape
        t = 'translate(%s,%s)' % (self.view_center[0], self.view_center[1] )
        
        # Make a nice useful name
        g_attribs = { inkex.addNS('label','inkscape'): 'koch' ,
                      inkex.addNS('transform-center-x','inkscape'): str(0),
                      inkex.addNS('transform-center-y','inkscape'): str(0),
                      'transform': t,
                      'style' : styles[1],
                      'info':'N: '+str(self.options.depth) }
        # add the group to the document's current layer
        topgroup = inkex.etree.SubElement(self.current_layer, 'g', g_attribs )


        NN = 2*self.options.depth
        NP = self.options.num_petals
        SF = 2*self.options.shrink_factor
        
        payload = []
        for y in range(-NP,NP):	
            mpts = [ff(z,ww=1./NP, ds=SF) for z in line(npts=NN, y0=y)]
            payload.append(mk_plugs(mpts))
            mpts = [ff(z,ww=1./NP, ds=SF) for z in line(npts=NN, y0=y,sgn=-1 )]
            payload.append(mk_plugs(mpts))
        
        payload = [pts2curve(cc) for cc in payload]
        payload = ' '.join(payload)
            
        curve_attribs = { 'style': styles[0],
                                      'd': payload}
        
        inkex.etree.SubElement(topgroup,
                                    inkex.addNS('path','svg'),
                                    curve_attribs )


if __name__ == '__main__':
    e = Myextension()
    e.affect()


