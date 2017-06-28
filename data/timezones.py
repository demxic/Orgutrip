#!/usr/bin/env python
# -*- coding: latin-1 -*-
from collections import namedtuple
import pytz

#carries the timepoint in seconds where extra credits start being calculated +
#plus multiplying factor for each one.
City = namedtuple("City", "timezone, payzone")


"""
Payzones
	[0:Bajo costo,
	 1:ACA
	 2:CUN-SJD
	 3:FRONTERA
	 4:USA, BOG, C.AMERICA, CUBA
	 5:JFK, LIM, CANADA, EZE
	 6:CDG, SCL, GRU, FCO
	 7:MAD, NRT, PVG               ]
"""

amount = [[167  ,   370,   370],
		[237   ,      464,   464],
		[301   ,      653,   653],
		['U$21.30','U$43.10','U$ 43.10'],
		['U$22.40','U$44.90','U$ 46.00'],
		['U$24','U$45.30','U$ 46.30'],
		['U$34.70', 'U$55.50', 'U$62.80'],
		['U$36.50', 'U$58.80', 'U$66.40']]

# VIATICUM DICTIONARY

PMX = pytz.timezone('America/Mazatlan')
MST = pytz.timezone('US/Mountain')
NMX = pytz.timezone('America/Santa_Isabel')
PST = pytz.timezone('US/Pacific')
CMX = pytz.timezone('America/Mexico_City')
CST = pytz.timezone('US/Central')
CNX = pytz.timezone('America/Cancun')
SMX = pytz.timezone('America/Hermosillo')
EST = pytz.timezone('US/Eastern')
COL = pytz.timezone('America/Bogota')
VEN = pytz.timezone('America/Caracas')
CAM = pytz.timezone('America/Guatemala')
AST = pytz.timezone('America/Blanc-Sablon')
PET = pytz.timezone('America/Lima')
ART = pytz.timezone('America/Buenos_Aires')
NAS = pytz.timezone('America/Nassau')
CET = pytz.timezone('Europe/Paris')
GMT = pytz.timezone('Europe/London')
CLT = pytz.timezone('Chile/Continental')
BRT = pytz.timezone('Brazil/East')
JST = pytz.timezone('Japan')
CHT = pytz.timezone('Asia/Shanghai')
PTY = pytz.timezone('America/Panama')

citiesDic ={"MEX" : City(CMX, 0),	"HMO" : City(SMX, 0), 	"CUU" : City(PMX, 0),	"CEN" : City(SMX, 0),	"LMM" : City(PMX, 0),
			"TRC" : City(CMX, 0),	"LAP" : City(PMX, 0),	"CUL" : City(PMX, 0), 	"DGO" : City(CMX, 0), 	"MTY" : City(CMX, 0),
			"SLW" : City(CMX, 0),	"MZT" : City(PMX, 0),	"ZCL" : City(CMX, 0),	"AGU" : City(CMX, 0), 	"SLP" : City(CMX, 0),
			"TAM" : City(CMX, 0),	"GDL" : City(CMX, 0),	"BJX" : City(CMX, 0), 	"QRO" : City(CMX, 0),	"PVR" : City(CMX, 0),
			"MLM" : City(CMX, 0), 	"PAZ" : City(CMX, 0), 	"CLQ" : City(CMX, 0),	"ZIH" : City(CMX, 0),	"VER" : City(CMX, 0),
			"PBC" : City(CMX, 0), 	"MTT" : City(CMX, 0), 	"OAX" : City(CMX, 0),	"HUX" : City(CMX, 0),	"VSA" : City(CMX, 0),
			"TAP" : City(CMX, 0), 	"MID" : City(CMX, 0),	"CPE" : City(CMX, 0), 	"CME" : City(CMX, 0), 	"CTM" : City(CMX, 0),
			"TGZ" : City(CMX, 0), 	"LTO" : City(PMX, 0),	"TLC" : City(CMX, 0),	"ZLO" : City(CMX, 0),
			"ACA" : City(CMX, 1),
			"CUN" : City(CNX, 2), 	"SJD" : City(CMX, 2),	"CZM" : City(CNX, 2),
			"TIJ" : City(PST, 3), 	"MXL" : City(PST, 3), 	"CJS" : City(PST, 3), 	"NLD" : City(CST, 3), 	"MAM" : City(CST, 3),
			"REX" : City(CST, 3),
			"SMF" : City(PST, 4), 	"SFO" : City(PST, 4), 	"OAK" : City(PST, 4), 	"SJC" : City(PST, 4), 	"SAN" : City(PST, 4),
			"FAT" : City(PST, 4),	"BSF" : City(PST, 4), 	"SNA" : City(PST, 4), 	"ONT" : City(PST, 4), 	"LAS" : City(PST, 4),
			"PHX" : City(SMX, 4), 	"DEN" : City(MST, 4),	"SAT" : City(CST, 4), 	"AUS" : City(CST, 4), 	"DFW" : City(CST, 4),
			"TUS" : City(SMX, 4), 	"IAH" : City(CST, 4), 	"ORD" : City(CST, 4),	"ATL" : City(EST, 4), 	"IAD" : City(EST, 4),
			"BOS" : City(EST, 4), 	"SEA" : City(EST, 4), 	"SLC" : City(MST, 4),	"MCO" : City(EST, 4), 	"MIA" : City(EST, 4),
			"BWI" : City(EST, 4), 	"LAX" : City(PST, 4), 	"IND" : City(EST, 4),	"MCI" : City(CST, 4),	"BHM" : City(CST, 4),
			"BOG" : City(COL, 4), 	"MDE" : City(COL, 4), 	"CCS" : City(VEN, 4),	"PTY" : City(PTY, 4),
			"MGA" : City(CAM, 4), 	"GUA" : City(CAM, 4), 	"SJO" : City(CAM, 4), 	"SAP" : City(CAM, 4), 	"SAL" : City(CAM, 4),
			"HAV" : City(EST, 4), 	"VRA" : City(EST, 4), 	"UIO" : City(CAM, 4),	"PUJ" : City(AST, 4), 	"SJU" : City(AST, 4),
			"MKE" : City(CST, 4),	"CVG" : City(EST, 4),	"LAN" : City(EST, 4),	"NAS" : City(NAS, 4),
			"JFK" : City(EST, 5), 	"LIM" : City(PET, 5), 	"EZE" : City(ART, 5), 	"YUL" : City(EST, 5), 	"YYZ" : City(EST, 5),
			"CDG" : City(CET, 6), 	"SCL" : City(CLT, 6), 	"GRU" : City(BRT, 6), 	"GIG" : City(BRT, 6), 	"FCO" : City(CET, 6),
			"MAD" : City(CET, 7), 	"NRT" : City(JST, 7), 	"PVG" : City(CHT, 7), 	"BCN" : City(CET, 7), 	"LHR" : City(GMT, 7),
			"   " : "   "}


# Trans destinations
transDest = ["MAD", "NRT", "CDG", "LHR", "PVG", "AMS", "FCO"]

asianCities = ['NRT', 'PVG', "ICN"]