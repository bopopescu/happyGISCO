[![DOI](https://zenodo.org/badge/125985870.svg)](https://zenodo.org/badge/latestdoi/125985870) 
happygisco
=========

Simple geoservice interface (API) on top of _Eurostat_ _GISCO_ web-services.
---

The project `happyGISCO` (pronounce as if you were French) provides with the implementation of a `Python` interface to [_GISCO_](http://ec.europa.eu/eurostat/web/gisco) web-services. The module `happygisco` will enable you to run some of the basic geographical operations supported by _GISCO_, *e.g.* geocoding, routing and NUTS identification. 

<table align="center">
    <tr> <td align="left"><i>documentation</i></td> <td align="left">available at: http://happygisco.readthedocs.io</td> </tr> 
    <tr> <td align="left"><i>status</i></td> <td align="left">since 2018 &ndash; <b>in construction</b></td></tr> 
    <tr> <td align="left"><i>contributors</i></td> 
    <td align="left" valign="middle">
<a href="https://github.com/gjacopo"><img src="https://github.com/gjacopo.png" width="40"></a>
</td> </tr> 
    <tr> <td align="left"><i>license</i></td> <td align="left"><a href="https://joinup.ec.europa.eu/sites/default/files/eupl1.1.-licence-en_0.pdfEUPL">EUPL</a> </td> </tr> 
</table>

This material accompanies the articles referenced below and illustrates the idea of **_Eurostat_ data as a service**. The rationale is further described in the paper _"Empowering and interacting with statistical produsers: A practical example with Eurostat data as a service"_.

**Quick install and start**

TBC

Once installed, the module can be imported simply:

```python
>>> import happygisco
```

**Usage**

###### Services

Some variants of the geolocation service are made available through the implementation of different classes:

* `OSMService`:  this is an interface to [_OpenStreetMap_](https://www.openstreetmap.org)  native **geocoding and routing web-services**;
* `GISCOService`: this is an interface to _Eurostat_ GISCO web-services; the geocoding and routing tools are also based on _OpenStreetMap_ (the class `GISCOService` derives from `OSMService`); it also enables the users to **retrieve the NUTS region at any level from any geolocation given by its toponame (place) or its geographical coordinates**;
* `APIService`: this calls other "external" geo- web-services (including  [_Google maps_](https://cloud.google.com/maps-platform/)), *e.g.* to **geolocate geographical features**.

Note that **no caching** is performed after running the services, unless the services are run from one of the features below.

It is pretty straigthforward to create such a service:

```python
>>> from happygisco import services
>>> service = services.GISCOService()
```

and run the supported methods:

```python
>>> place =  ''Lampedusa, Italia"
>>> coord = service.place2coord(place, unique=True)
>>> print(coord)
[35.511134150000004, 12.59629135962961]
>>> alt_place = service.coord2place(coord)
>>> print(alt_place)
'Strada di Ponente, Lampedusa e Linosa, (Sicily), Italy'
>>> nuts = service.coord2nuts(coord, level=2)
>>> print(nuts)
{'attributes': {'CNTR_CODE': 'IT', 'LEVL_CODE': '2', 'NAME_LATN': 'Sicilia',
  'NUTS_ID': 'ITG1',  'NUTS_NAME': 'Sicilia',  'OBJECTID': '320',
  'SHRT_ENGL': 'Italy'},
 'displayFieldName': 'NUTS_ID',
 'layerId': 2, 'layerName': 'NUTS_2013',
 'value': 'ITG1'}
 ```

###### Features

It is possible to create **simple geographical features whose methods implement and apply the different services defined above**, *e.g.*:

* a `Location`: a feature representing a geolocation, *i.e.* defined as a topo/placename or as a list of geographical coordinates,
* an `Area`: a simple vector geometry () in the sense of _GISCO_ services expressed as a dictionary, *i.e.*, structured like the JSON file returned by the  `GISCO` geocoding or reverse geocoding services,
* a `NUTS`: the vector geometry representing a NUTS area expressed as a dictionary, *i.e.*, structured like the JSON file returned by the  `GISCO` `findnuts` services.

One can for instance declare a specific location, and run any of the supported methods (for a quick check of the geodesic distance calculation, have a look at [this](https://www.timeanddate.com/worldclock/distanceresult.html?p1=195&p2=133) for instance):

```python
>>> from happygisco import features
>>> location =  features.Location(place="Lisbon, Portugal")
>>> location.coord
[38.7077507, -9.1365919]
>>> location.routing('Paris, France')
({'distance': 3058767.9, 'duration': 377538.2,
  'geometry': 'uv}qEaeqhEo_XlbOutDa`~@uuVocZqa|@ttDqaZneRwcjEetxBwfYags@}_nAugsAmaYcmcApxCiiuDcvi@webB`dFeix@q}VqdvAfaj@greAtqEuwi@c~QmvqCuhZ}o`AzzVkv{@egOo|Vjf@avyCrlZocsFwo_@ef`DgdKkqQ{gPbkA{pUgwq@h{[s}`B`hJsgnBaq^oMetAkab@q~j@at~@hbd@yheAhmh@gad@vyz@dit@uxz@kjt@knh@lbd@ibd@xheAp~j@`t~@dtAjab@`q^nMahJrgnBe|[x}`BvqU`wq@nkPsgAt_KlnQdo_@r}_DwkZlksFkg@joyCdhOjzVk{V|f|@vhZph`Ab~Q`vqCsnEjpi@wdj@tyeAx|Vd`vA_cF~mx@~ui@tebB_yCtguD~aYjocAn`nAhgsAtfYrgs@pdjEbrxBhaZieR~a|@{tD`vV|cZ~}F`_}@nuUaaN',
  'legs': [{'distance': 1530444.4, 'duration': 188741.1,
    'steps': [], 'summary': ''},
   {'distance': 1528323.5, 'duration': 188797.1, 'steps': [], 'summary': ''}]},
 [{'hint': 'DcOGgEuuRIQAAAAAAAAAAE0AAAAAAAAASgQAAOofZwBScQAAzuv3AcpmDwImok4CMZZ0_wAAAQEZfn5e',
   'location': [33.024974, 34.563786], 'name': ''},
  {'hint': 'mRIbgp0SG4IAAAAAAAAAAFoAAAAAAAAAogIAADJYZwFScQAAeuyjAgCdNAIifukCi-EjAAAAAQEZfn5e',
   'location': [44.297338, 37.002496], 'name': ''},
  {'hint': 'DcOGgEuuRIQAAAAAAAAAAE0AAAAAAAAASgQAAOofZwBScQAAzuv3AcpmDwLU3csCvrFGAAAAAQEZfn5e',
   'location': [33.024974, 34.563786], 'name': ''}])
>>> location.findnuts(level=3)
{'CNTR_CODE': 'PT', 'LEVL_CODE': '3',
 'NAME_LATN': '�rea Metropolitana de Lisboa', 'NUTS_ID': 'PT170',
 'NUTS_NAME': '�rea Metropolitana de Lisboa', 'OBJECTID': '1233',
 'SHRT_ENGL': 'Portugal'}
>>> location.distance('Paris, France')
1455.7107037157618
```

What about creating a NUTS object:

```python 
>>> nuts = features.NUTS()
```

###### Tools

**Geospatial tools are derived from [`gdal`](http://gdal.org) methods** and provided in the `GDALTool` class. 

These tools can be used, for instance, with NUTS appropriate vector data sources to operate the NUTS identification. Note that it is a brute-force solution, since the program will explore sequentially all NUTS features so as to identify the correct region. This could be improved using a multithread process for instance, _e.g._ using [`multiprocessing`](https://docs.python.org/3.4/library/multiprocessing.html?highlight=process) module. Besides, the program does not check the validity of the result returned by _Google maps_ services, since this result can be ambiguous and/or inaccurate.

**Notebook examples**

Simple examples are available in the form of _Jupyter_ notebooks under the [_notebooks/_](https://github.com/eurostat/happyGISCO/tree/master/notebooks) folder, *e.g.*:

* a [basic use]( https://cdn.rawgit.com/eurostat/happyGISCO/c7153073/notebooks/Example%20of%20Eurostat%20'Data%20as%20a%20Service'%20using%20happyGISCO%20module.html) of the geocoding services,
* an example of features definition and geocoding,
* an extended workflow for location identification and retrieval. 

**<a name="Resources"></a>Resources**

* _Eurostat_ NUTS [bulk data source](http://ec.europa.eu/eurostat/cache/GISCO/distribution/v2/nuts/download/ref-nuts-2013-01m.shp.zip) and [how to](http://ec.europa.eu/eurostat/documents/4311134/4366152/guidelines-geographic-data.pdf) interpret it.
* _Eurostat_  GISCO webservices: [_find-nuts_](http://europa.eu/webtools/rest/gisco/nuts/find-nuts.py) and [_geocode_](http://europa.eu/webtools/rest/gisco/api?).
* `gdal` [package](https://pypi.python.org/pypi/GDAL) and [cookbook](https://pcjericks.github.io/py-gdalogr-cookbook/index.html).
* Geo packages: [`googlemaps`](https://pypi.python.org/pypi/googlemaps/) and [`geopy`](https://github.com/geopy/geopy).

**<a name="References"></a>References**

* Grazzini J., Museux J.-M. and Hahn M. (2018): [**Empowering and interacting with statistical produsers: A practical example with Eurostat data as a service**](), submitted to _Conference of European Statistics Stakeholders_.
* Grazzini J., Lamarche P., Gaffuri J. and Museux J.-M. (2018): [**"Show me your code, and then I will trust your figures": Towards software-agnostic open algorithms in statistical production**](https://www.researchgate.net/publication/325320551_Show_me_your_code_and_then_I_will_trust_your_figures_Towards_software-agnostic_open_algorithms_in_statistical_production), in Proc.  _Quality Conference_.

