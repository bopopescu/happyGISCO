#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. settings.py

Basic definitions for NUTS datasets and webservices.

**About**

*credits*:      `grazzja <jacopo.grazzini@ec.europa.eu>`_ 

*version*:      0.1
--
*since*:        Sat Mar 31 21:54:08 2018

**Contents**
"""

import os, sys#analysis:ignore
import inspect#analysis:ignore

#%%
#==============================================================================
# CLASSES Error/Warning/Verbose
#==============================================================================

class nutsError(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, msg, expr=None):    
        self.msg = msg
        if expr is not None:    self.expr = expr
        Exception.__init__(self, msg)
    def __str__(self):              return repr(self.msg)

class nutsWarning(Warning):
    """Base class for warnings in this module."""
    def __init__(self, msg, expr=None):    
        self.msg = msg
        if expr is not None:    self.expr = expr
        # logging.warning(self.msg)
    def __repr__(self):             return self.msg
    def __str__(self):              return repr(self.msg)

class nutsVerbose(object):
    """Base class for verbose printing mode in this module."""
    def __init__(self, msg, expr=None, verb=True):    
        self.msg = msg
        if verb is True:
            print('\n[verbose] - %s' % self.msg)
        if expr is not None:    self.expr = expr
    def __repr__(self):             return self.msg
    def __str__(self):              return repr(self.msg)

#%%
#==============================================================================
# GLOBAL VARIABLES
#==============================================================================

PACKAGE             = "place2nuts"

PROTOCOLS           = ('http', 'https', 'ftp')
"""
Recognised protocols (API, bulk downloads,...).
"""
DEF_PROTOCOL        = 'http'
PROTOCOL            = DEF_PROTOCOL
"""
Default protocol used by the API.
"""
LANGS               = ('en','de','fr')
"""
Languages supported by this package.
"""
DEF_LANG            = 'en'
"""
Default language used when launching Eurostat API.
"""

EC_URL              = 'europa.eu'
"""
European Commission URL.
"""
GISCO_DOMAIN        = 'webtools/rest/gisco/'
"""
GISCO domain under European Commission URL.
"""
GISCO_URL           = '%s/%s' % (EC_URL, GISCO_DOMAIN)
"""
GISCO complete URL.
"""

CODER_GISCO         = 'gisco'
KEY_GISCO           = None
CHECK_TYPE          = True
CHECK_OSM_KEY       = True

CODER_GOOGLE        = 'GoogleV3'
CODER_GOOGLE_MAPS   = 'GMaps'
CODER_GOOGLE_PLACES = 'GPlace'
KEY_GOOGLE          = 'key'

CODER_GEONAME       = 'GeoNames'

CODER_LIST          = [CODER_GISCO, CODER_GOOGLE, CODER_GOOGLE_MAPS, CODER_GOOGLE_PLACES]
CODER_PROJ          = {CODER_GISCO: 'WGS84',
                       CODER_GOOGLE: 'EPSG3857',
                       CODER_GOOGLE_MAPS: 'EPSG3857', 
                       CODER_GOOGLE_PLACES: 'EPSG3857'}

DRIVER_NAME         = '' # 'ESRI Shapefile'
                       
VERBOSE             = True

#%%
#==============================================================================
# CLASS _geoDecorators
#==============================================================================
    
class _geoDecorators(object):
    """Base class with dummy decorators used to parse and check place and coordinate 
    arguments, and not only, used in the various methods of the geolocation services 
    classes.
    """
    
    KW_PLACE        = 'place'
    KW_LAT          = 'lat'
    KW_LON          = 'lon'
    KW_COORD        = 'coord'
    KW_PROJECTION   = 'proj' 
    
    #/************************************************************************/
    class __parse(object):
        """Base parsing class for geographical entities. All decorators in 
        :class:`_geoDecorators` will inherit from this class.
        """
        def __init__(self, func, obj=None, cls=None, method_type='function'):
            self.func, self.obj, self.cls, self.method_type = func, obj, cls, method_type     
        def __get__(self, obj=None, cls=None):
            if self.obj == obj and self.cls == cls:
                return self 
            if self.method_type=='property':
                return self.func.__get__(obj, cls)
            method_type = ( # note that we added 'property'
                'staticmethod' if isinstance(self.func, staticmethod) else
                'classmethod' if isinstance(self.func, classmethod) else
                'property' if isinstance(self.func, property) else 
                'instancemethod'
                )
            return object.__getattribute__(self, '__class__')( 
                self.func.__get__(obj, cls), obj, cls, method_type) 
        #def __get__(self, obj, objtype):
        #    # support instance methods
        #    return functools.partial(self.__call__, obj)
        def __getattribute__(self, attr_name): 
            try:
                return object.__getattribute__(self, attr_name) 
            except AttributeError:
                return getattr(self.func, attr_name)
        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_place(__parse):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with place (topo,geo) names to functions and methods.
        """
        def __call__(self, *args, **kwargs):
            if args not in (None,()):      
                if all([isinstance(a,str) for a in args]):
                    place = args
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    place = args[0]
                else:   
                    raise IOError('input arguments not recognised')
            else:                           
                place = kwargs.pop('place', None)
            if place in (None,[],''):
                raise IOError('no input arguments passed')
            if not isinstance(place,(list,tuple)):
                place = [place,]
            if not all([isinstance(p,str) for p in place]):
                raise IOError('wrong format for input place')
            return self.func(place, **kwargs)

    #/************************************************************************/
    class parse_coordinate(__parse):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with :literal:`(lat,lng)` geographical coordinates to functions and methods.
        """
        def __call__(self, *args, **kwargs):
            coord, lat, lon = None, None, None
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    coord = args
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if len(args[0])==2 and all([isinstance(args[0][i],(tuple,list)) for i in (0,1)]):
                        lat, lon = args[0]
                    elif all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        coord = args[0]
                elif len(args) == 1 and isinstance(args[0],(tuple,list)) and len(args[0])==2:
                    lat, lon = args[0]
                elif len(args) == 2                                         \
                    and all([isinstance(args[i],(tuple,list)) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    lat, lon = args
                else:   
                    raise IOError('input coordinate arguments not recognised')
            else:   
                coord = kwargs.pop('coord', None)         
                lat = kwargs.pop('lat', None) or kwargs.pop('x', None)
                lon = kwargs.pop('lon', None) or kwargs.pop('y', None)
            try:
                assert not(coord is None and lat is None and lon is None) 
            except AssertionError:
                raise IOError('no input coordinate arguments passed')
            try:
                assert coord is None or (lat is None and lon is None)
            except AssertionError:
                raise IOError('too many input coordinate arguments')
            if coord is not None:
                if not isinstance(coord,(list,tuple)):  
                    coord = [coord]
                try:
                    assert all(['lat' in c and 'lon' in c for c in coord])
                except AssertionError:
                    raise IOError('wrong dictionary keys for input coordinate argument')
                try:
                    lat, lon = [_ for _ in zip(*[(c['lat'], c['lon']) for c in coord])]
                except:
                    raise IOError('wrong input coordinate argument passed')
            if lat is None or lon is None:
                raise IOError('wrong geographical coordinates')
            lat, lon = [lat,], [lon,]
            if not len(lat) == len(lon):
                raise IOError('incompatible geographical coordinates')
            return self.func(lat, lon, **kwargs)
       
    #/************************************************************************/
    class parse_place_or_coordinate(__parse):
        """
        """
        def __call__(self, *args, **kwargs):
            try:
                place = _geoDecorators.parse_place(lambda p, **kw: p)(*args, **kwargs)
            except:
                place = None
            else:
                kwargs.update({'place': place})
            try:
                lat, lon = _geoDecorators.parse_coordinate(lambda l, L, **kw: [l, L])(*args, **kwargs)
            except:
                lat, lon = None, None
            else:
                kwargs.update({'lat': lat, 'lon': lon})
            try:
                assert not(place in ('',None) and lat in ([],None) and lon in ([],None))
            except:
                raise IOError('no geographical entity parsed to define the place')
            try:
                assert place in ('',None) or (lat in ([],None) and lon in ([],None))
            except:
                raise IOError('too many geographical entities parsed to define the place')
            return self.func(*args, **kwargs)
        
    #/************************************************************************/
    class parse_nuts(__parse):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with NUTS information stored in GISCO-like formatted dictionary (from JSON 
        response) to functions and methods.
        """
        KW_RESULTS      = 'results'
        KW_ATTRIBUTES   = 'attributes'
        KW_LEVEL        = 'LEVL_CODE'
        def __call__(self, *args, **kwargs):
            level = kwargs.pop('level',None)
            nuts = None
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    nuts = args
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        nuts = args[0]
            else:   
                nuts = kwargs.pop('nuts', None)                  
            if nuts is None:
                # raise IOError('no NUTS parsed')
                return self.func(*args, **kwargs)
            if not isinstance(nuts,(list,tuple)):
                nuts = [nuts,]
            if not all([isinstance(n,dict) and self.KW_ATTRIBUTES in n for n in nuts]): 
                raise IOError('NUTS attribtues not recognised')
            if level is not None:
                nuts = [n for n in nuts if n[self.KW_ATTRIBUTES][self.KW_LEVEL] == str(level)]
            kwargs.update({'nuts': nuts}) 
            return self.func(**kwargs)

    #/************************************************************************/
    class parse_geometry(__parse):
        """Generic class decorator used to parse (positional,keyword) arguments 
        with :literal:`(lat,lng)` geographical coordinates stored in GISCO-like
        formatted dictionary (from JSON response) to functions and methods.
        """
        KW_FEATURES     = 'features'
        KW_GEOMETRY     = 'geometry'
        KW_PROPERTIES   = 'properties'
        KW_TYPE         = 'type'
        KW_OSM_KEY      = 'osm_key'
        KW_COORDINATES  = 'coordinates'
        def __call__(self, *args, **kwargs):
            coord = None
            if args not in (None,()):      
                if all([isinstance(a,dict) for a in args]):
                    coord = args
                elif len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if all([isinstance(args[0][i],dict) for i in range(len(args[0]))]):
                        coord = args[0]
            else:   
                coord = kwargs.pop('coord', None)        
            if coord is not None:
                if isinstance(coord,(list,tuple)) and all([isinstance(c,dict) for c in coord]):      
                    coord_ = [c for c in coord                                                               \
                       if self.KW_GEOMETRY in c and self.KW_PROPERTIES in c and self.KW_TYPE in c                 \
                       and c[self.KW_TYPE]=='Feature'                                                 \
                       and (not(CHECK_TYPE) or c[self.KW_GEOMETRY][self.KW_TYPE]=='Point')         \
                       and (not(CHECK_OSM_KEY) or c[self.KW_PROPERTIES][self.KW_OSM_KEY]=='place') \
                       ]
                    coord = coord[0] if coord_==[] else coord_[0]  
                    coord = dict(zip(['lon','lat'],coord[self.KW_GEOMETRY][self.KW_COORDINATES]))
                kwargs.update(coord) 
                return self.func(**kwargs)
            else:
                return self.func(*args, **kwargs)
        
    #/************************************************************************/
    class parse_projection(__parse):
        """Generic class decorator used to parse keyword argument with projection 
        information to functions and methods.
        """
        PROJECTION      = {'WGS84': 4326, 4326: 4326,
                           4258: 4258,
                           'EPSG3857': 3857, 3857: 3857, 
                           'LAEA': 3035, 3035: 3035}
        def __call__(self, *args, **kwargs):
            proj = kwargs.pop('proj', 'WGS84')
            if proj not in list(self.PROJECTION.keys() | self.PROJECTION.values()):
                raise IOError('projection %s not supported' % proj)
            kwargs.update({'proj': self.PROJECTION[proj]})                  
            return self.func(*args, **kwargs)
        
    #/************************************************************************/
    class parse_year(__parse):
        """Generic class decorator used to parse keyword year argument used for  
        NUTS definition.
        """
        YEARS      = [2006, 2013, 2010, # 2016 ?
                      ]
        def __call__(self, *args, **kwargs):
            year = kwargs.pop('year', 2013)
            if year not in tuple(self.YEARS):
                raise IOError('year %s not supported' % year)
            kwargs.update({'year': year})                  
            return self.func(*args, **kwargs)

    #/************************************************************************/
    class parse_file(__parse):
        """
        """
        def __call__(self, *args, **kwargs):
            dirname, basename, filename = None, None, None
            if args not in (None,()):      
                if len(args) == 1 and isinstance(args[0],(tuple,list)):
                    if len(args[0])==2 and all([isinstance(args[0][i],str) for i in (0,1)]):
                        dirname, basename = args[0]
                    elif all([isinstance(args[0][i],str) for i in range(len(args[0]))]):
                        filename = args[0]
                elif len(args) == 1 and isinstance(args[0],str) and len(args[0])==2:
                    dirname, basename = args[0]
                elif len(args) == 2                                         \
                    and all([isinstance(args[i],str) or not hasattr(args[i],'__len__') for i in (0,1)]):    
                    dirname, basename = args
                else:   
                    raise IOError('input file arguments not recognised')
            else:   
                dirname = kwargs.pop('dir', '')         
                basename = kwargs.pop('base', '')
                filename = kwargs.pop('file', '')
            try:
                assert not(filename in ('',None) and basename in ('',None))
            except AssertionError:
                raise IOError('no input file arguments passed')
            try:
                assert filename in ('',None) or basename in ('',None)
            except AssertionError:
                raise IOError('too many input file arguments')
            if filename is None:
                try:
                    filename = os.path.join(os.path.realpath(dirname or ''), basename)
                except:
                    raise IOError('wrong input file argument passed')
            if not isinstance(filename,str):
                filename = [filename,]
            return self.func(filename, **kwargs)
    
        



