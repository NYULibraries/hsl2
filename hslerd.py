from lxml import etree as ET
from lxml.builder import ElementMaker
from xml.dom import minidom
from StringIO import StringIO
import codecs
import csv
import sys

E = ElementMaker(namespace="http://www.openarchives.org/OAI/2.0",
				nsmap = {None: "http://www.openarchives.org/OAI/2.0"})
O = ElementMaker(namespace="http://www.openarchives.org/OAI/2.0/oai_dc/",
				nsmap = {'oai_dc': "http://www.openarchives.org/OAI/2.0/oai_dc/"})
D = ElementMaker(namespace="http://purl.org/dc/elements/1.1/",
				nsmap = {'dc': "http://purl.org/dc/elements/1.1/"})
T = ElementMaker(namespace="http://purl.org/dc/terms/",
				nsmap = {'dcterms': "http://purl.org/dc/terms/"})
N = ElementMaker(namespace="http://purl.org/nyu/digicat/",
				nsmap = {'nyu': "http://purl.org/nyu/digicat/"})

schemaloc = ("http://www.openarchives.org/OAI/2.0/ "
						"http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd")

OAI = getattr(E, 'OAI-PMH')

LIST = E.ListRecords

xml = OAI(
	LIST()
)

listrecs = xml.find("{http://www.openarchives.org/OAI/2.0}ListRecords")
xml.set('oai_dc', 'http://www.openarchives.org/OAI/2.0/oai_dc/')
xml.set('dc', 'http://purl.org/dc/elements/1.1/')
xml.set('dcterms', 'http://purl.org/dc/terms/')
xml.set('nyucore', 'http://purl.org/nyu/digicat/')

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
	# csv.py doesn't do Unicode; encode temporarily as UTF-8:
	csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
													dialect=dialect, **kwargs)
	for row in csv_reader:
		# decode UTF-8 back to Unicode, cell by cell:
		yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
	for line in unicode_csv_data:
		yield line.encode('utf-8')

fn = sys.argv[1]
ofn = sys.argv[2]
data =  codecs.open(fn, 'r', encoding='utf-8')
reader = unicode_csv_reader(data)
for r in reader:
	## This is the bit that handles all the mapping to NYU core.
	## Uses Element Makers above. 
	## D = dc; T = dcterms; N = nyucore
	## first we'll do a bit of extra parsing on our issns & isbns
	
	pissbn = r[4]
	if len(pissbn) in [8,9]:
		pissn = pissbn + " (print)"
		pisbn = ""
		print pisbn + "|" + pissn
	elif len(pissbn) not in [8,9,0,3]:
		pisbn = pissbn + " (print)"
		pissn = ""
		print pisbn + "|" + pissn
	else:
		pisbn = ""
		pissn = ""
	
	eissbn = r[5]
	if len(eissbn) in [8,9]:
		eissn = eissbn + " (electronic)"
		eisbn = ""
	elif len(eissbn) not in [8,9,0,3]:
		eisbn = eissbn + " (electronic)"
		# + str(len(eissbn))
		eissn = ""
	else:
		eisbn = ""
		eissn = ""

	record = E.record(
		E.header(
			E.identifier(str(r[0].encode('utf-8')))
		),
		E.metadata(
			O.dc(
				D.identifier(str(r[0])),
				D.title(r[1]),
				T.alternative(r[2]),
				N.accessURL(r[3]),
				N.isbn(eisbn),
				N.isbn(pisbn),
				N.issn(eissn),
				N.issn(pissn),
				D.contributor(r[6]),
				D.type(r[8]),
				D.subject(r[9]),
				N.availability(r[10]),
				N.vendor(r[13]),
				D.description(r[14]),
				N.processing('HSLERD')
			)
		)
	)
	
	listrecs.append(record)

	xml.attrib['{{{pre}}}schemaLocation'.format(pre="http://www.w3.org/2001/XMLSchema-instance")] = schemaloc

# This stuff isn't really necessary.
# Is there in a (failed) attempt to get all namespace declarations on root element
# lxml is a pain in the a$$ that way...
parser = ET.XMLParser(ns_clean=True)
xml_string = ET.tostring(xml)
xml_clean = ET.parse(StringIO(xml_string), parser)
outfile = open(ofn, 'w')
xml_clean.write(outfile, xml_declaration=True, encoding='utf-8', pretty_print=True)

