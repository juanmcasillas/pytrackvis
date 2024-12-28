# coding=latin-1
#
# ^^^ Put this in order to suppor the Latin-1 encoding of the Catastro XML data
# catastro.py
# interface with the spanish catastro

#
# http://www.catastro.meh.es/ayuda/lang/castellano/servicios_web.htm
# https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx?op=Consulta_DNPRC
# http://www.catastro.meh.es/ws/webservices_catastro.pdf
#
# examples
# http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_RCCOOR?SRS=EPSG:4258&Coordenada_X=-4.266139&Coordenada_Y=40.392238
# http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC?Provincia=&Municipio=&RC=28099A00709004
#


import xml.dom.minidom as xmlp
import hashlib
import os
import io
import ssl 
import urllib3
from collections import namedtuple
from .helpers import point_inside_polygon,C
import copy 
import json

from .geojson import GeoJSON

class GenericCache:
    """
    Cache a URL using a MD5 hash for the entire string.
    if key is passed, the file is stored using KEY instead
    the HASH (useful to store things with some criteria)
    """

    def __init__(self,cachedir, unsafe_ssl=True):
        self.cachedir = cachedir
        self.queries = 0.0
        self.hits = 0.0
        self.unsafe_ssl = unsafe_ssl
        self.print_info = False
        self.always_get = False

    def PrintStats(self):

        print("Cache Manager Stats")
        print("=" * 80)
        print("Total queries: ", self.queries)
        print("Cache Hits:", self.hits)
        print("Eficency: %3.2f %%" % float((self.hits*100/self.queries)))


    def Lookup(self, url, key=None):
        self.queries += 1

        # fix windows-unix issue
        cc = self.cachedir.split("/")

        if not key:
            itemkey = hashlib.md5(str(url).encode('utf-8')).hexdigest()

        else:
            itemkey = key

        cachedir = cc + [ itemkey ]

        urlp = os.sep.join(cachedir)

        if os.path.exists(urlp) and self.always_get == False:
            fd = open(urlp,"rb")
            r = fd.read()
            fd.close()
            if self.print_info: print("[C*]")
            self.hits += 1
            return r

        # not found in cache
        # get and save


        if self.print_info: print (url)

        if self.unsafe_ssl:
            custom_ssl_context = ssl.create_default_context()
            custom_ssl_context.check_hostname = False
            custom_ssl_context.verify_mode = ssl.CERT_NONE
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            http = urllib3.PoolManager(cert_reqs=None, ssl_context=custom_ssl_context)
        else:
            http = urllib3.PoolManager()

        resp = http.request("GET",url)
        data_file = io.BytesIO(resp.data)

        # store
        if self.always_get == False:
            dirp = os.path.dirname(urlp)
            if not os.path.exists(dirp):
                os.makedirs(dirp)

            fcache = open(urlp,"wb+")
            data = data_file.read()
            fcache.write(data)
            fcache.close()
            if self.print_info: print ("[C-]")
        return data



class CatastroInfo:
    codigo_provicia = 0
    codigo_municipio = 0

    nombre_provincia = ""
    nombre_municipio = ""
    nombre_paraje    = ""
    domicilio_tributario = ""
    calificacion_catastral = ""
    denominacion_clase = ""

    xml = ""
    def __init__(self, xml_string):

        self.xml2attr = {
                'cp': "codigo_provincia",
                'cn': "tipo_de_bien",
                'cm': "codigo_municipio",
                'np': "nombre_provincia",
                'nm': "nombre_municipio",
                'npa': "nombre_paraje",
                'ldt': "domicilio_tributario",
                'ccc': "calificacion_catastral",
                'dcc': "denominacion_clase",
                'nv': "nombre_via",
                'cv': "codigo_via",
                'tv': "tipo_via",
                'luso': "utilizacion_uso"
                }

        #print xml_string

        dom = xmlp.parseString(xml_string)

        for element in self.xml2attr.keys():
            data = self._xml_gData(dom,element)
            self.__dict__[self.xml2attr[element]] = data

        self.xml = xml_string

    def _xml_gData(self, dom, nodename):
        node = dom.getElementsByTagName(nodename)

        if not node:
            return None

        node = node[0]

        return self._xml_gTEXT(node)


    def _xml_gTEXT(self,nodelist):
        rc = []
        for node in nodelist.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def __str__(self):
        s = """codigo_provicia = %s
codigo_municipio = %s
nombre_provincia = %s
nombre_municipio = %s
nombre_paraje    = %s
domicilio_tributario = %s
calificacion_catastral = %s
denominacion_clase = %s
""" % (self.codigo_provicia, self.codigo_municipio, self.nombre_provincia, self.nombre_municipio,
       self.nombre_paraje, self.domicilio_tributario, self.calificacion_catastral, self.denominacion_clase)
        return s
    

    def as_dict(self):
        r = {
            'codigo_municipio': self.codigo_municipio,
            'nombre_provincia': self.nombre_provincia,
            'nombre_municipio': self.nombre_municipio,
            'nombre_paraje': self.nombre_paraje,
            'domicilio_tributario': self.domicilio_tributario,
            'calificacion_catastral': self.calificacion_catastral,
            'denominacion_clase': self.denominacion_clase,
        }
        return r
    
class CatastroManager:

    OVC_host = "https://ovc.catastro.meh.es"
    OVC_url = "/ovcservweb/OVCSWLocalizacionRC/"
    # cords used in WGS80 (WGS84)
    OVCCoordenadas_url = "OVCCoordenadas.asmx/Consulta_RCCOOR?SRS=EPSG:4258&Coordenada_X={longitude}&Coordenada_Y={latitude}"
    # rc is the concatenation of PC items.
    #<pc>
    #    <pc1>28099A0</pc1>
    #    <pc2>0709004</pc2>
    #</pc>
    # RC = {pc1}{pc2} = 28099A00709004
    OVCCallejero_url = "OVCCallejero.asmx/Consulta_DNPRC?Provincia=&Municipio=&RC={rc}"

    class_styles = {}
    class_styles['C-']      = "#33cccc" #LABOR O LABRADO SECANO
    class_styles['E-']      = "#66ffff" #PASTOS
    class_styles['O-']      = "#66AAAA" #OLIVOS DE SECANO
    class_styles['FE']      = "#336600" #ENCINAR
    class_styles['HC']      = "#900010" #HIDROGRAFA CONSTRUIDA
    class_styles['HG']      = "#A00010" #HIDROGRAFA NATURAL
    class_styles['I-']      = "#303080" #IMPRODUCTIVO
    class_styles['MB']      = "#33cc66" #MONTE BAJO
    class_styles['PD']      = "#00cc66" #PRADOS O PRADERAS
    class_styles['CR']      = "#00EE90" #LABOR O REGADIO
    class_styles['FR']      = "#00FFA0" #FRUTALES REGADIO
    class_styles['V-']      = "#006699" #VID SECANO
    class_styles['VT']      = "#406020" #VIA DE COMUNICACION DE DOMINIO PUBLICO
    class_styles['VO']      = "#00AA99" #VI�A OLIVAR SECANO
    class_styles['MM']      = "#30AA90" #PINAR MADERABLE
    class_styles['MP']      = "#30AAAA" #PINAR PINEA O DE FRUTO
    class_styles['NC']      = "#66f090" #PARAJE
    class_styles['MR']      = "#66f040" #PARAJE
    class_styles['CE']      = "#44f020" #PARAJE

    class_styles['123']     = "#907060" # RECOLETOS
    class_styles['127']     = "#907060" # RECOLETOS
    class_styles['270']     = "#557580" # DELESPINO
    class_styles['10']      = "#407080" # CORREDERA
    class_styles['12']      = "#506070" # HOSPITAL
    class_styles['36']      = "#506070" # HOSPITAL
    class_styles['50']      = "#407080" # MARTIRES DE EL TIEMBLO
    class_styles['35']      = "#407080" # GENERALISIMO FRANCO
    class_styles['RI']      = "#805070" #
    class_styles['PR']      = "#807080" #
    class_styles['HR']      = "#40BBCC" #UMBRIA - SEVILLA
    class_styles['EU']      = "#40A0D0" #REHOYO - SEVILLA
    class_styles['FS']      = "#40A0D0" #REHOYO - SEVILLA

    class_styles['9']       = "#902070" #FUENTE NUEVA
    class_styles['2']       = "#902070" #CONCEPCION
    class_styles['13']      = "#902070" #IGLESIA
    class_styles['20']      = "#667070" #TENERIA
    class_styles['47']      = "#667070" #EXTRARRADIO
    class_styles['F-']      = "#667070" #EXTRARRADIO
    class_styles['MT']      = "#667070" #EXTRARRADIO
    class_styles['PR']      = "#667070" #EXTRARRADIO
    class_styles['80']      = "#667070" #EXTRARRADIO
    class_styles['EE']      = "#669090" #PASTOS CON ENCINAS
    class_styles['MF']      = "#22AA55" #ESPECIES MEZCLADAS
    class_styles['FF']      = "#404040" #VIA FERREA
    class_styles['EO']      = "#009988" #PASTOS CON OLIVOS

    class_styles['84']      = "#405070" #DISEMINADO
    class_styles['85']      = "#306090" #VI�UELAS

    class_styles['GE']      = "#50AA66" #generico # not used ?
    class_styles['DES']     = "#8000AA" #desconocido
    class_styles['PRI']     = "#700020" #privado

    class_styles['AM']        = "#500010" #PARAJE
    class_styles['560']       = "#500010" #CASTILLO
    class_styles['78']        = "#500010" #RONCESVALLES
    class_styles['90024']     = "#500010" #SECTOR-5

    def __init__(self, cachedir, unsafe_ssl = True):
        self.unsafe_ssl = unsafe_ssl
        self.cachedir = cachedir
        self.cache = GenericCache(cachedir, self.unsafe_ssl)

    def GetRC(self, point):

        # <?xml version="1.0" encoding="utf-8"?>
        # <consulta_coordenadas xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.catastro.meh.es/">
        #   <control>
        #     <cucoor>1</cucoor>
        #     <cuerr>0</cuerr>
        #   </control>
        #   <coordenadas>
        #     <coord>
        #       <pc>
        #         <pc1>28099A0</pc1>
        #         <pc2>0709004</pc2>
        #       </pc>
        #       <geo>
        #         <xcen>-4.266139</xcen>
        #         <ycen>40.392238</ycen>
        #         <srs>EPSG:4258</srs>
        #       </geo>
        #       <ldt>Pol�gono 7 Parcela 9004 CAMINO SERVICIO. NAVAS DEL REY (MADRID)</ldt>
        #     </coord>
        #   </coordenadas>
        # </consulta_coordenadas>

        # is changed !!!
        lon,lat = point

        url = self._base_url() + "/" + CatastroManager.OVCCoordenadas_url
        url = url.format(latitude=lat, longitude=lon )

   
        rc = []
        data = self._get_url_data(url)
        dom = xmlp.parseString(data)
        # check for error

        error_code = dom.getElementsByTagName("cod")
        if error_code:
            error_code = dom.getElementsByTagName("cod")[0]
            error_num = self._xml_gTEXT(error_code)

            if error_num:
                # no ref about this X,Y: a Public Space. (road, via, etc)
                return None

        pc = dom.getElementsByTagName("pc")
        if not pc:
            return None
        pc = pc[0]
        for i in pc.childNodes:
            if i.nodeType == i.ELEMENT_NODE:
                x = self._xml_gTEXT(i)
                rc.append(x)

        rc = ''.join(rc)
        return rc

    def GetInfo(self,rc):
        # <?xml version="1.0" encoding="utf-8"?>
        # <consulta_dnp xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.catastro.meh.es/">
        #   <control>
        #     <cudnp>1</cudnp>
        #     <cucul>1</cucul>
        #   </control>
        #   <bico>
        #     <bi>
        #       <idbi>
        #         <cn>RU</cn>
        #         <rc>
        #           <pc1>28099A0</pc1>
        #           <pc2>0709004</pc2>
        #           <car>0000</car>
        #           <cc1>F</cc1>
        #           <cc2>W</cc2>
        #         </rc>
        #       </idbi>
        #       <dt>
        #         <loine>
        #           <cp>28</cp>
        #           <cm>99</cm>
        #         </loine>
        #         <cmc>99</cmc>
        #         <np>MADRID</np>
        #         <nm>NAVAS DEL REY</nm>
        #         <locs>
        #           <lors>
        #             <lorus>
        #               <czc>0</czc>
        #               <cpp>
        #                 <cpo>7</cpo>
        #                 <cpa>9004</cpa>
        #               </cpp>
        #               <npa>CAMINO SERVICIO</npa>
        #               <cpaj>83</cpaj>
        #             </lorus>
        #           </lors>
        #         </locs>
        #       </dt>
        #       <ldt>Pol�gono 7 Parcela 9004 CAMINO SERVICIO. NAVAS DEL REY (MADRID)</ldt>
        #       <debi>
        #         <sfc>0</sfc>
        #       </debi>
        #     </bi>
        #     <lspr>
        #       <spr>
        #         <cspr>0</cspr>
        #         <dspr>
        #           <ccc>I-</ccc>
        #           <dcc>IMPRODUCTIVO</dcc>
        #           <ip>00</ip>
        #           <ssp>12861</ssp>
        #         </dspr>
        #       </spr>
        #     </lspr>
        #   </bico>
        # </consulta_dnp>

        url = self._base_url() + "/" + CatastroManager.OVCCallejero_url
        url = url.format(rc=rc)

        rc = []
        
        data = self._get_url_data(url)

        info = CatastroInfo(data)
        return info


    def _base_url(self):

        url = CatastroManager.OVC_host + "/" + CatastroManager.OVC_url
        return url

    def _get_url_data(self,url, key=None):

        data = self.cache.Lookup(url, key)

        # don't use direct calls, use cache instead
        #fd = urllib.urlopen(url)
        #data = fd.read()
        #fd.close()

        return data

    def _xml_gTEXT(self,nodelist):
        rc = []
        for node in nodelist.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)


    def getRCCoords(self, rc):
        """
        using a non-documented feature from Catastro, we can export the
        file to KML without asking for a captcha

        URL
        https://ovc.catastro.meh.es/Cartografia/WMS/BuscarParcelaGoogle3D.aspx?refcat=28099A009090030000FM&tipo=3d
        returns a valid KML format.

        The interesting DATA is here (in Polygon->outerBoundaryIs->LinearRing->coordinates)
        <Placemark>
<name>28099A009090030000FM</name>
            <styleUrl>#linea_parcela</styleUrl>
            <Polygon>
                <tessellate>1</tessellate>
                <outerBoundaryIs>
                    <LinearRing>
                        <coordinates>
-4.25032148764138,40.3951963081146,0 -4.25038466616851,40.3949790569016,0 -4.25038986972915,40.3949609829493,0 -4.25041003791375,40.3948916625365,0 -4.25094002234089,40.3920120959572,0 -4.25099359376574,40.391723233368,0 -4.25105146505493,40.3913487357005,0 -4.25085079082086,40.3913283847889,0 -4.25083580900696,40.3917925067971,0 -4.25062196477979,40.3929523707011,0 -4.25055203536836,40.3933315884977,0 -4.25045996008011,40.3934497037962,0 -4.2503432408678,40.3935095235644,0 -4.25024235905654,40.3934700702076,0 -4.2501480872649,40.3935140617476,0 -4.25011385937198,40.3935300171325,0 -4.25014975162777,40.3936040465729,0 -4.25018122716369,40.3936689302373,0 -4.25025118349864,40.3939474478229,0 -4.25025799001736,40.3939969228389,0 -4.25029127299556,40.3942037662352,0 -4.25026409022832,40.3946454978108,0 -4.25025854422542,40.394676908543,0 -4.25020014937842,40.395011047199,0 -4.25017763982854,40.3951127346214,0 -4.25001528438246,40.395846368044,0 -4.24999321657494,40.395927690671,0 -4.24990005413258,40.3964013915263,0 -4.24956109748225,40.3981256618688,0 -4.24947471949906,40.398565420199,0 -4.24938877422184,40.3990028269605,0 -4.24929312312704,40.3994892609725,0 -4.24929544845914,40.3996153594952,0 -4.24934154631269,40.3998397218094,0 -4.24939751040781,40.3999539841491,0 -4.24946713564746,40.4000869227737,0 -4.2495156168933,40.4001597307027,0 -4.2495515981998,40.4002065480994,0 -4.24959603308089,40.400264445066,0 -4.24963099114079,40.4002941567178,0 -4.24967349146063,40.4003302731928,0 -4.24976974511781,40.4004120284053,0 -4.24978511142808,40.4004209612159,0 -4.24980262339052,40.4004312221542,0 -4.24983276196233,40.4004488239214,0 -4.24985718214742,40.4004630641444,0 -4.24986635382154,40.400468370291,0 -4.24992091263815,40.40050021225,0 -4.2499801179255,40.4005347966843,0 -4.25001156587966,40.400553104954,0 -4.25001990454453,40.4005579696532,0 -4.25009674714613,40.4005904714765,0 -4.25010031824561,40.400592414806,0 -4.25010924266258,40.4005970929885,0 -4.25017704810856,40.4006251880593,0 -4.2501878559049,40.4006297557817,0 -4.25028715398726,40.4006721946314,0 -4.25034748506188,40.4006911814248,0 -4.25045309480956,40.4007244529528,0 -4.25047278376288,40.4007313569755,0 -4.2504831036678,40.4007350290642,0 -4.25048165821917,40.4007333330205,0 -4.25084421829392,40.400846350108,0 -4.25096850777135,40.4008765362363,0 -4.2517450356591,40.4011293919492,0 -4.2519825024945,40.4012259177699,0 -4.25200871734432,40.4012415795114,0 -4.25204303546969,40.4012621083476,0 -4.2522267789217,40.4013719224002,0 -4.25326327556788,40.4022031111809,0 -4.25327439964513,40.4022119994195,0 -4.25343493169267,40.4023408014878,0 -4.25436130516775,40.4030469604102,0 -4.25456444024946,40.4031979107833,0 -4.25474168499702,40.4032872466616,0 -4.2547673798254,40.4033002107627,0 -4.25486183159117,40.4033478332621,0 -4.25514710764924,40.4034798688512,0 -4.25542707965861,40.4036434967087,0 -4.25575443205764,40.4038201179793,0 -4.25599266750487,40.4039571713078,0 -4.25629604007271,40.404111529481,0 -4.25659958161657,40.4042748983369,0 -4.25687956031396,40.4044385180485,0 -4.25706553462965,40.4046166724697,0 -4.25718545108591,40.4047279832861,0 -4.25731874239222,40.4049247278009,0 -4.25747227323619,40.4051961153011,0 -4.25748981970107,40.4052270949652,0 -4.25754416747172,40.4053231729483,0 -4.25775773489683,40.4057172377083,0 -4.25781318747373,40.405790326544,0 -4.25781657037371,40.4057947941479,0 -4.25795102598331,40.4059718904967,0 -4.25795466738064,40.4059759994353,0 -4.25803404077493,40.4061403934965,0 -4.2580610247224,40.4062357825116,0 -4.25806847051334,40.4062742682335,0 -4.2580699219246,40.4063522102385,0 -4.25807480826263,40.4063548236751,0 -4.25806541694149,40.4063963394035,0 -4.25802001130923,40.4064995700461,0 -4.25806416929081,40.4064723648737,0 -4.25807133226417,40.40645832326,0 -4.25809160968628,40.4063827843844,0 -4.25809351456997,40.4063648361092,0 -4.25809950385581,40.4063067541502,0 -4.25809406418485,40.4062487965633,0 -4.25809376312243,40.4062452864008,0 -4.25807929797042,40.4061899494981,0 -4.25804767079027,40.4061116466872,0 -4.25801410399025,40.4060430944953,0 -4.25808945847559,40.4061280384431,0 -4.25839443945579,40.4063679617539,0 -4.25836870947496,40.4063845297581,0 -4.25842207328929,40.4063985612033,0 -4.25854028017686,40.4064582956744,0 -4.25868308507139,40.406552338057,0 -4.25879589689297,40.4066080635202,0 -4.25891653989162,40.4066555641304,0 -4.25901922808329,40.4066944900647,0 -4.25927397873689,40.406768290423,0 -4.25927196407872,40.406660206577,0 -4.25927926368069,40.4066212630342,0 -4.25917106877992,40.4065919691745,0 -4.25900766018784,40.4065347591026,0 -4.25887892604632,40.4064739235542,0 -4.25883308188851,40.4064491980566,0 -4.25869347617729,40.4063835978966,0 -4.25856135488962,40.406291470707,0 -4.2584483165393,40.406223545032,0 -4.25838162926471,40.4061651775857,0 -4.25837874705277,40.4061717763854,0 -4.25829756490927,40.4061045668521,0 -4.25812913508705,40.4059643038338,0 -4.25804932954715,40.4058602420848,0 -4.25789432722621,40.4056454828214,0 -4.25773972504052,40.405346130682,0 -4.25771021315969,40.4052889889897,0 -4.25769836261879,40.4052743704725,0 -4.25757414254231,40.4050322989639,0 -4.25745937794083,40.4048239660964,0 -4.25745805047248,40.4048311560597,0 -4.25743093739346,40.4047752899728,0 -4.25733808971015,40.4046481583275,0 -4.25722442521153,40.4045362346475,0 -4.25704646910633,40.4043763983191,0 -4.25693955141023,40.4043375976604,0 -4.25693065284299,40.4043343611426,0 -4.25658470041999,40.4041083923865,0 -4.25650126491364,40.4040705973221,0 -4.25632167784033,40.4039632674782,0 -4.25623323661509,40.4039195762869,0 -4.25622484498682,40.4039210998724,0 -4.25617131421291,40.4038985919095,0 -4.25614434481666,40.4038814348526,0 -4.25610564817279,40.4038603782613,0 -4.25596170766684,40.4037820833622,0 -4.25590007459599,40.4037462221295,0 -4.25583038869294,40.403714574378,0 -4.2557060367655,40.4036402104323,0 -4.25563733279011,40.403600831337,0 -4.25545994922877,40.4035114262822,0 -4.25530836790448,40.4034350243052,0 -4.25526780179558,40.4034125823518,0 -4.25502623793717,40.40328711745,0 -4.25484302128265,40.4031836714444,0 -4.25471931501113,40.4031138218435,0 -4.25464411651528,40.4030482879469,0 -4.2545921753662,40.4030132712589,0 -4.2544042745237,40.4028865830633,0 -4.25434118628244,40.4028388991805,0 -4.25428789867998,40.4027986222948,0 -4.25415923049555,40.4027013625145,0 -4.25410445512662,40.4026599620652,0 -4.25386087673585,40.4024758420659,0 -4.25356046959342,40.4022519601789,0 -4.25334225114517,40.4020702532225,0 -4.25309629013872,40.4018654506179,0 -4.25287150850201,40.401664251219,0 -4.25266906575568,40.4015098264013,0 -4.25240752174355,40.4013255330683,0 -4.25238506982155,40.4012627189911,0 -4.25237629627307,40.401220098673,0 -4.25221987087385,40.4011078899171,0 -4.25221469138011,40.401107864937,0 -4.25211482603407,40.4010908748288,0 -4.25200807495546,40.4010727159833,0 -4.25200557407936,40.4010716169623,0 -4.25148391995669,40.4009021557821,0 -4.25130692984315,40.4008489059458,0 -4.25097749706804,40.4007344958552,0 -4.25068269448918,40.4006491780854,0 -4.25043945521513,40.4005633559337,0 -4.25024927782535,40.4004962563823,0 -4.25017846527102,40.4004645317805,0 -4.25017363704323,40.4004678857261,0 -4.24996989491307,40.4003586269228,0 -4.24982149493023,40.4002483596035,0 -4.24968602647967,40.4001176148762,0 -4.24960548240732,40.3999652001934,0 -4.24956963396323,40.3998704408787,0 -4.24952151431243,40.3997432562569,0 -4.2495068868153,40.3996433082061,0 -4.2494967570029,40.3995740676957,0 -4.24949008213418,40.3995763289798,0 -4.24951169522831,40.3994680930145,0 -4.24963836505228,40.3988338309495,0 -4.24971515280782,40.3983814512055,0 -4.24983520599406,40.3978244660589,0 -4.24987956547418,40.3974900380238,0 -4.24995898318511,40.3971800097376,0 -4.25006202018259,40.3965642363859,0 -4.25015199042482,40.3961056101865,0 -4.2501791649353,40.3959895122555,0 -4.25019578480729,40.3959146627966,0 -4.25024315054698,40.395656907768,0 -4.25023751938168,40.3956576037843,0 -4.25024949386269,40.3955918404115,0 -4.25032148764138,40.3951963081146,0 -4.25032148764138,40.3951963081146,0                         </coordinates>
                    </LinearRing>
                </outerBoundaryIs>
            </Polygon>
        </Placemark>

        1) get the data.
        2) parse the XML
        3) return the position, in WGS84 (as googleEarth). List of coords.
        """



        KML_host = "http://ovc.catastro.meh.es"
        KML_url = "Cartografia/WMS/BuscarParcelaGoogle3D.aspx?refcat={rc}&tipo=3d"

        url = KML_host + '/' + KML_url.format(rc=rc)
        data = self._get_url_data(url,rc)

        dom = xmlp.parseString(data)
        # check for error
        if not dom:
            return None

        # lookup the name with the catastral reference to extract the polygon

        placemark =  dom.getElementsByTagName("Placemark")
        if not placemark:
            return None

        found = False
        for p in placemark:
            name =  p.getElementsByTagName("name")
            for item in name:
                ntext = self._xml_gTEXT(item)
                if ntext == rc:
                    found = True
                    dom = p
                    break
            if found: break


        poly = dom.getElementsByTagName("Polygon")
        if not poly:
            return None


        opoly = poly[0]
        outer =  opoly.getElementsByTagName("outerBoundaryIs")
        if not outer:
            return None

        outer = outer[0]
        linear = outer.getElementsByTagName("LinearRing")
        if not linear:
            return None
        linear = linear[0]
        coords = linear.getElementsByTagName("coordinates")
        if not coords:
            return None
        coords = coords[0]

        retval = self._xml_gTEXT(coords)
        data = []
        if retval:
            retval = retval.split()
            data = []
            for i in retval:
                (lon,lat,elevation) = i.split(',')
                data.append( (lon,lat,elevation))


        # if we have inner... process it. #####handle with caution
        # diseminated blocks more of the time.
        # google maps eats the coordinates happily xD


        ipoly = poly[0]
        inner =  ipoly.getElementsByTagName("innerBoundaryIs")
        if not inner:
            return data

        inner = inner[0]
        linear = inner.getElementsByTagName("LinearRing")
        if not linear:
            return None

        linear = linear[0]
        coords = linear.getElementsByTagName("coordinates")
        if not coords:
            return None
        coords = coords[0]
        retval = self._xml_gTEXT(coords)

        ##data = []
        if retval:
            retval = retval.split()
            ##data = []
            for i in retval:
                (lon,lat,elevation) = i.split(',')
                data.append( (lon,lat,elevation))

        #if rc == "28042A02400010":
        #    for d in data:
        #        print "%s,%s,0 " % (d[0],d[1])
        #    sys.exit(0)
        return data

    def isPublic(self, rc):

        # 28099A01209011  {HC} HIDROGRAF�A CONSTRUIDA (EMBALSE,CANAL..)
        # 28099A01209001  {VT} V�A DE COMUNICACI�N DE DOMINIO P�BLICO
        # 9xxx last four digits, if start with 9, are public. If rc is None,
        # also is public
        # changed after talk with Fernando Alonso & J. Vaquero.
        # 5-Feb-16
        if rc == None: return True

        if len(rc) != 14: raise Exception("Bad RC") # some is wrong with this.

        rccode = rc[10]
        #print rccode, rc
        #28037A03209013
        if rccode == '9': return True

        return False




        #if key in ['VT', 'DPU']:
        #    return True
        #return False

        # more elaborated code here:

        #if not key in [ 'DES','PRI' ]:
        #    return True
        #return False

    def map_class(self, cls):
        styles = {}
        # colors: #AAbbggrr

        if cls in self.class_styles.keys():
            return self.class_styles[cls]
        else:
            return  "#EE0000" # default


    def check_point(self, lat, lon, debug=True):
    
        # only works one time, so there is no problem interating the thing, I suppose.
        lat = float(lat)
        lon = float(lon)
        
        polygons = {}
        polygons_ordered = []
      

        point = C(latitude=lat, longitude=lon, elevation=0.0)
        # check if the point is inside the poly, or what
        # if we have stored polys, try if we are inside. If not, work on

        rc = self.GetRC((point.longitude, point.latitude))
        ccc = None      # code of land
        cdc = None      # description
        is_p = False

        if not rc:
            is_p = True
            msg =  "%f,%f DOMINIO PUBLICO (carretera, calle, etc.)" % (point.latitude, point.longitude)
            ccc = "DPU" # Dominio Public Use
            cdc = "DOMINIO PUBLICO"
        else:

            # ask for RC data. Note about agregates, and so on.

            info = self.GetInfo(rc)

            ccc = info.calificacion_catastral or None # desconocido
            cdc = info.denominacion_clase or None

            if info.calificacion_catastral and info.denominacion_clase:
                #e.g VT, vias publicas
                ccc = info.calificacion_catastral
                cdc = info.denominacion_clase

            if info.domicilio_tributario:
                ccc = ccc or "PRI"
                cdc = info.domicilio_tributario

            if not info.domicilio_tributario and info.nombre_via:
                ccc = info.codigo_via
                cdc = info.nombre_via

            if not cdc and info.nombre_paraje: cdc = info.nombre_paraje

            if not ccc: ccc = "DES"
            if not cdc: cdc = "DESCONOCIDO"

            msg =  "[%s] %f,%f %s(%s) {%s} %s" % (rc, point.latitude, point.longitude,  info.nombre_provincia, info.nombre_municipio, ccc, cdc)

            coords = self.getRCCoords(rc)
            if coords:
                if not rc in polygons.keys():
                    polygons[rc] = msg
                    polygons_ordered.append({ 'msg': msg, 'coords': coords, 
                                                'ccc': ccc, 'cdc': cdc, 
                                                'info': info.as_dict(), 
                                                'rc': rc,
                                                'is_public': is_p or self.isPublic(rc),
                                                'style': self.map_class(ccc) })
                                        # missing point, point

        # add fields and build the real thing.
        o = {
            'latitude' : point.latitude,
            'longitude': point.longitude,
            'elevation': point.elevation,
            'catastro': {
                'is_public': is_p or self.isPublic(rc),
                'rc': rc,
                'ccc': ccc,
                'cdc': cdc
            }
        }

        return o, polygons_ordered



    def check_pointlist(self, points):

        polygons = {}
        polygons_ordered = []
        last_polygon = None
        track_segments = []
        debug_segments = False
        segstate = "out"
        segkind = False
        segment = []
        segment_coords = []

        #for point in
        
        for pindex in range(len(points)):
          
            point = points[pindex]

            # check if the point is inside the poly, or what
            # if we have stored polys, try if we are inside. If not, work on

            rc = None
            cached = False

            if last_polygon:
                pcoords = list(last_polygon.values())[1] # coords

                #msg, coords, ccc, cdc, info, point, rc = last_poly

                if point_inside_polygon(point, pcoords):

                    #msg, coords, ccc, cdc, info, pointx, rc, is_p, _ = list(last_polygon.values())
                    # point is overwritten here.
                    msg, coords, ccc, cdc, info, rc, is_p, _ = list(last_polygon.values())
                    
                    msg = msg + "[POLY]"
                    cached = True

            # if data is not cached by previous polygon,
            # then ask for things.

            if not cached:

                rc = self.GetRC((point.longitude, point.latitude))
                ccc = None      # code of land
                cdc = None      # description
                is_p = False

                if not rc:
                    is_p = True
                    msg =  "%f,%f DOMINIO PUBLICO (carretera, calle, etc.)" % (point.latitude, point.longitude)
                    ccc = "DPU" # Dominio Public Use
                    cdc = "DOMINIO PUBLICO"
                else:

                    # ask for RC data. Note about agregates, and so on.

                    info = self.GetInfo(rc)

                    ccc = info.calificacion_catastral or None # desconocido
                    cdc = info.denominacion_clase or None

                    if info.calificacion_catastral and info.denominacion_clase:
                        #e.g VT, vias publicas
                        ccc = info.calificacion_catastral
                        cdc = info.denominacion_clase

                    if info.domicilio_tributario:
                        ccc = ccc or "PRI"
                        cdc = info.domicilio_tributario

                    if not info.domicilio_tributario and info.nombre_via:
                        ccc = info.codigo_via
                        cdc = info.nombre_via

                    if not cdc and info.nombre_paraje: cdc = info.nombre_paraje

                    if not ccc: ccc = "DES"
                    if not cdc: cdc = "DESCONOCIDO"

                    msg =  "[%s] %f,%f %s(%s) {%s} %s %s" % (rc, point.latitude, point.longitude,  info.nombre_provincia, info.nombre_municipio, ccc, cdc, is_p)

                    coords = self.getRCCoords(rc)
                    if coords:
                        if not rc in polygons.keys():
                            polygons[rc] = msg
                            #polygons_ordered.append([msg, coords, ccc, cdc, info, point, rc])
                            polygons_ordered.append({ 'msg': msg, 'coords': coords, 
                                                  'ccc': ccc, 'cdc': cdc, 
                                                  'info': info.as_dict(), 
                                                  #'point': point,
                                                  'rc': rc,
                                                  'is_public': is_p or self.isPublic(rc),
                                                  'style': self.map_class(ccc) })

                        #last_polygon = [msg, coords, ccc, cdc, info, point, rc]
                        last_polygon = { 'msg': msg, 'coords': coords, 
                                     'ccc':ccc, 'cdc': cdc, 'info': 
                                     info.as_dict(), 
                                     #'point': point,
                                     'rc': rc,
                                     'is_public': is_p or self.isPublic(rc),
                                     'style': self.map_class(ccc) }

            # ANALIZE BY CATEGORY and STATE.
            if debug_segments:
                print("N] ",msg.encode('ASCII','xmlcharrefreplace'))

            # add fields

            points[pindex].catastro = C()
            points[pindex].catastro.rc = rc
            points[pindex].catastro.ccc = ccc
            points[pindex].catastro.cdc = cdc
            points[pindex].catastro.is_public = is_p or self.isPublic(rc)

            # process segments
            # if same state
            
            p = points[pindex]
            
            if segstate == "out":
                segstate = "in"
                segkind = p.catastro.is_public
                segment.append(p)
                segment_coords.append([ p.latitude, p.longitude, p.elevation ])
                if debug_segments: 
                    print( "IN ", p.catastro.rc, p.catastro.ccc, p.catastro.cdc, segkind)
                continue

            if segstate == "in" and p.catastro.is_public != segkind:
                segstate = "out"
                
                p2 = copy.copy(p)
                p2.catastro.is_public = segkind
                
                segkind = p.catastro.is_public
                
                # copy the point avoid skip gaps.
                segment.append(p2)
                segment_coords.append([ p2.latitude, p2.longitude, p2.elevation ])
                track_segments.append(( segment[-1].catastro.rc, segment[-1].catastro.ccc, segment[-1].catastro.cdc, segment[-1].catastro.is_public, segment, segment_coords ))
                segment = []
                segment_coords = []
                segment.append(p)
                segment_coords.append([ p.latitude, p.longitude, p.elevation ])
                if debug_segments:
                    print ("OUT", p.catastro.rc, p.catastro.ccc, p.catastro.cdc, segkind)
                continue

            if segstate == "in" and p.catastro.is_public == segkind:
                segment.append(p)
                segment_coords.append([ p.latitude, p.longitude, p.elevation ])
                if debug_segments: 
                    print ("---", p.catastro.rc, p.catastro.ccc, p.catastro.cdc, segkind)
                continue

        # if there is something in the segment add it
        if segstate == "in" and len(segment) > 0:
            track_segments.append(( segment[-1].catastro.rc, segment[-1].catastro.ccc, segment[-1].catastro.cdc, segment[-1].catastro.is_public, segment, segment_coords ))
            if debug_segments: 
                print ("OUT", segment[-1].catastro.rc, segment[-1].catastro.ccc, segment[-1].catastro.cdc, segkind)
        

        return points, track_segments, polygons_ordered




    def check_point_as_geojson(self, lat, lng):
        # maplibre do some coord swapping (lat long) so put the thing right.
        data, poly = self.check_point(lat, lng)
        
        features = []
        for p in poly:
            coords = list(map(lambda x: [ float(x[0]), float(x[1]), float(x[2])], p['coords']))
            t = copy.copy(p)
            del t['coords']
            
            features.append(GeoJSON.polygon_feature(coords, t, id=t['rc']))

        return data, GeoJSON.feature_collection(features = features)



    def check_pointlist_as_geojson(self, points, public_color="#20FF20", private_color="#FF2020"):
        points, track_segments, poly = self.check_pointlist(points)
        
        # first, create the poly features.
        features = []
        for p in poly:
            coords = list(map(lambda x: [ float(x[0]), float(x[1]), float(x[2])], p['coords']))
            t = copy.copy(p)
            del t['coords']
            features.append(GeoJSON.polygon_feature(coords, t, id=t['rc']))

        # second add the line segments, styling then.
        
        count_public = 1
        count_private = 1
    
        for segment in track_segments:
            rc, ccc, cdc, is_public, segment, segment_coords = segment
            style = private_color # private 
            count = count_public

            if is_public:
                 style = public_color # public 
                 count = count_private

            coords = list(map(lambda x: [ float(x[1]), float(x[0]), float(x[2])], segment_coords))
            prop = {
                'rc': rc,
                'ccc': ccc,
                'is_public': is_public,
                'style': style
            }

            features.append(GeoJSON.line_feature(coords, prop))


        return GeoJSON.feature_collection(features=features)



















# class KMLFile:
#     def __init__(self, route_name, position, outputname):
#         self.route_name = route_name
#         self.position   = position
#         self.outputname = outputname



#     def Create(self, polygons, gpx=""):

#         header = self._genHeader(self.route_name, self.position.longitude, self.position.latitude)

#         data = "<Folder><name>Informaci�n Catastral</name>"

#         #for rc in polygons.keys():
#         # format
#         # polygons_ordered.append( msg, coords, ccc, cdc, info, point, rc )
#         #                           0       1   2       3   4       5   6
#         for item in polygons:

#             (msg, coords, ccc, cdc, info, point, rc) = item

#             #
#             # build a well formed message and description
#             #

#             curl = "https://www1.sedecatastro.gob.es/OVCFrames.aspx?TIPO=CONSULTA"

#             pname = "<![CDATA[<b>RC[%s]</b></br>%s(%s)</br>CC: %s</br>]]>" %\
#              (rc, info.nombre_provincia, info.nombre_municipio,ccc)

#             pdesc = "<![CDATA[%s</br>Paraje: %s</br></br><a href='%s'>Web Catastro</a>]]>" %(cdc, info.nombre_paraje or "-", curl)

#             pdata = self._genKMLPolygon(rc, coords, pname, pdesc, ccc)
#             data += pdata

#         data += "</Folder>"

#         # add gpx if found
#         data += gpx

#         data = header + data + self._genFooter()


#         fout = open(self.outputname,"w")
#         fout.write(data)
#         fout.close()

#     def GPXWP2Kml(self, waypoints, style="gpxwaypoint"):

#             wpkml = """
#               <Placemark>
#                 <name>{name}</name>
#                 <description>{description}</description>
#                 <styleUrl>#{style}</styleUrl>
#                 <Point>
#                   <extrude>0</extrude>
#                   <altitudeMode>clampToGround</altitudeMode>
#                   <coordinates>{longitude},{latitude}</coordinates>
#                 </Point>
#               </Placemark>
#               """

#             if len(waypoints) == 0:
#                 return ""

#             r_kml = "<Folder><name>Puertas - Candados - Vallas</name>"
#             for wp in waypoints:
#                 r_kml += wpkml.format(style=style,
#                                       name=wp.name.encode('ASCII','xmlcharrefreplace'),
#                                       description=wp.description.encode('ASCII','xmlcharrefreplace'),
#                                       longitude=wp.longitude, latitude=wp.latitude)

#             r_kml += "</Folder>"
#             return r_kml

#     def GPX2KMLPlacemark(self, points, style="gpxtrack", gname="GPX track name", gdesc="GPX Track description"):
#         """
#         create a Placemark KML compliant value.
#         """

#         placemark = """
#                     <Placemark>
#                     <visibility>1</visibility>
#                     <open>0</open>
#                     <styleUrl>#{style}</styleUrl>
#                     <name>{gname}</name>
#                     <description>{gdesc}</description>
#                     <LineString>
#                         <extrude>true</extrude>
#                         <tessellate>true</tessellate>
#                         <altitudeMode>clampToGround</altitudeMode>
#                         <coordinates>
#                             {coordinates}
#                         </coordinates>
#                     </LineString>
#                 </Placemark>
#         """

#         coordinates = []
#         for p in points:
#             coordinates.append( ",".join([ str(p.longitude), str(p.latitude), str(p.elevation)]))

#         coordinates = " ".join(coordinates)

#         return placemark.format(style=style,
#                                 gname=gname.encode('ASCII','xmlcharrefreplace'),
#                                 gdesc=gdesc.encode('ASCII','xmlcharrefreplace'),
#                                 coordinates=coordinates)


#     def _genKMLPolygon(self, rc, coords, pname, desc, ccc):

#         poly="""
#              <Placemark>
#                 <name>{pname}</name>
#                 <description>{desc}</description>
#                 <styleUrl>#{ccc}</styleUrl>
#                 <Polygon>
#                     <tessellate>1</tessellate>
#                     <outerBoundaryIs>
#                         <LinearRing>
#                         <coordinates>
#                         {coords}
#                         </coordinates>
#                     </LinearRing>
#                 </outerBoundaryIs>
#             </Polygon>
#             </Placemark>
#             """

#         lines = []
#         for l in coords:
#             d = ','.join(l)
#             lines.append(d)

#         return poly.format(pname=pname.encode('ASCII','xmlcharrefreplace'),
#                            desc=desc.encode('ASCII','xmlcharrefreplace'),
#                            rc=rc, ccc=ccc, coords=' '.join(lines))



#     def _genStyles(self):
#         styles = {}
#         # colors: #AAbbggrr

#         styles['C-']      = "7033cccc" #LABOR O LABRADO SECANO
#         styles['E-']      = "7066ffff" #PASTOS
#         styles['O-']      = "7066AAAA" #OLIVOS DE SECANO
#         styles['FE']      = "70336600" #ENCINAR
#         styles['HC']      = "70900010" #HIDROGRAFA CONSTRUIDA
#         styles['HG']      = "70A00010" #HIDROGRAFA NATURAL
#         styles['I-']      = "70303080" #IMPRODUCTIVO
#         styles['MB']      = "7033cc66" #MONTE BAJO
#         styles['PD']      = "7000cc66" #PRADOS O PRADERAS
#         styles['CR']      = "7000EE90" #LABOR O REGADIO
#         styles['FR']      = "7000FFA0" #FRUTALES REGADIO
#         styles['V-']      = "70006699" #VID SECANO
#         styles['VT']      = "70406020" #VIA DE COMUNICACION DE DOMINIO PUBLICO
#         styles['VO']      = "7000AA99" #VI�A OLIVAR SECANO
#         styles['MM']      = "7030AA90" #PINAR MADERABLE
#         styles['MP']      = "7030AAAA" #PINAR PINEA O DE FRUTO
#         styles['NC']      = "7066f090" #PARAJE
#         styles['MR']      = "7066f040" #PARAJE
#         styles['CE']      = "7044f020" #PARAJE

#         styles['123']     = "70907060" # RECOLETOS
#         styles['127']     = "70907060" # RECOLETOS
#         styles['270']     = "70557580" # DELESPINO
#         styles['10']      = "70407080" # CORREDERA
#         styles['12']      = "70506070" # HOSPITAL
#         styles['36']      = "70506070" # HOSPITAL
#         styles['50']      = "70407080" # MARTIRES DE EL TIEMBLO
#         styles['35']      = "70407080" # GENERALISIMO FRANCO
#         styles['RI']      = "70805070" #
#         styles['PR']      = "70807080" #
#         styles['HR']      = "7040BBCC" #UMBRIA - SEVILLA
#         styles['EU']      = "7040A0D0" #REHOYO - SEVILLA
#         styles['FS']      = "7040A0D0" #REHOYO - SEVILLA

#         styles['9']      = "70902070" #FUENTE NUEVA
#         styles['2']      = "70902070" #CONCEPCION
#         styles['13']      = "70902070" #IGLESIA
#         styles['20']      = "70667070" #TENERIA
#         styles['47']      = "70667070" #EXTRARRADIO
#         styles['F-']      = "70667070" #EXTRARRADIO
#         styles['MT']      = "70667070" #EXTRARRADIO
#         styles['PR']      = "70667070" #EXTRARRADIO
#         styles['80']      = "70667070" #EXTRARRADIO
#         styles['EE']      = "70669090" #PASTOS CON ENCINAS
#         styles['MF']      = "7022AA55" #ESPECIES MEZCLADAS
#         styles['FF']      = "70404040" #VIA FERREA
#         styles['EO']      = "70009988" #PASTOS CON OLIVOS

#         styles['84']      = "70405070" #DISEMINADO
#         styles['85']      = "70306090" #VI�UELAS

#         styles['GE']      = "7050AA66" #generico # not used ?
#         styles['DES']     = "708000AA" #desconocido
#         styles['PRI']     = "70700020" #privado

#         styles['AM']     = "60500010" #PARAJE
#         styles['560']     = "60500010" #CASTILLO
#         styles['78']     = "60500010" #RONCESVALLES
#         styles['90024']     = "60500010" #SECTOR-5


#         style ="""
#         <Style id="{id}">
#             <LineStyle>
#                 <color>ff000000</color>
#                 <width>1</width>
#             </LineStyle>
#             <PolyStyle>
#                 <color>{color}</color>
#                 <fill>1</fill>
#             </PolyStyle>
#         </Style>
#         """

#         s = ""
#         for k in styles.keys():
#             s += style.format(id=k, color=styles[k])

#         # add special styles.

#         s += """<Style id="gpxtrack">
#             <LineStyle>
#                 <color>8000A000</color>
#                 <width>3</width>
#             </LineStyle>
#             </Style>

#             <Style id="gpxtrackpublic">
#             <LineStyle>
#                 <color>FFFF0000</color>
#                 <width>5</width>
#             </LineStyle>
#             </Style>

#             <Style id="gpxtrackprivate">
#             <LineStyle>
#                 <color>ff0000F8</color>
#                 <width>5</width>
#             </LineStyle>
#             </Style>

#             <Style id="gpxwaypoint">
#               <IconStyle>
#                 <scale>0.9</scale>
#                 <Icon>
#                   <href>http://maps.google.com/mapfiles/kml/pal3/icon34.png</href>
#                 </Icon>
#               </IconStyle>
#             </Style>

#         """

#         return s


#     def _genHeader(self, rname, longitude, latitude):


#         head = """<?xml version="1.0" encoding="ISO-8859-1"  ?>
#         <kml xmlns="http://www.opengis.net/kml/2.2">
#         <Document>
#             <name>{route_name}</name>
#             {styles}
#             <Visible>1</Visible>
#             <LookAt>
#                 <longitude>{longitude}</longitude>
#                 <latitude>{latitude}</latitude>
#                 <range>2442.36591410061</range>
#                 <tilt>45</tilt>
#                 <heading>0</heading>
#             </LookAt>
#         """

#         return head.format(route_name=rname, styles=self._genStyles(), longitude=longitude, latitude=latitude)

#     def _genFooter(self):
#         footer ="""
#         </Document>
#         </kml>
#         """
#         return footer

# class EmptyClass:
#     def __init__(self):
#         pass

if __name__ == "__main__":


    #cc = GenericCache("cache/xml")
    #print cc.Lookup(sys.argv[1])
    #sys.exit(0)

    Point = (40.392238,-4.266139)

    catastro = CatastroManager()
    rc = catastro.GetRC(Point)
    info = catastro.GetInfo(rc)

    print(info.nombre_paraje)
    print(info.domicilio_tributario)



