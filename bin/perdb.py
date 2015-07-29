import os
import xlrd
import madgetech.madgetech_2 as mt2

def loadPERdict():
    try:
    #Open the PER Meta Data excel spreadsheet and create a dictionary with serial's as the key and
    #various meta data as the value.
        workbook = xlrd.open_workbook('.\PER Logger Data.xlsx')
        sheet = workbook.sheet_by_index(0)

        PERdict = {}

        for rx in [r for r in range(sheet.nrows) if r > 1]:
            r = sheet.row(rx)
            if r[0].value!='':
                serial = r[0].value
                site = r[1].value
                location = r[2].value
                project = r[3].value
                startDateTuple = xlrd.xldate.xldate_as_tuple(r[4].value,workbook.datemode)
                endDateTuple = xlrd.xldate.xldate_as_tuple(r[5].value,workbook.datemode)
                timeZone = r[6].value
                sensorType = r[7].value
                condition = r[8].value
                climate = r[9].value
                coord = (r[10].value,r[11].value)
                chl = r[12].value
                sul = r[13].value
                notes = r[14].value
                PERdict[serial] = [site,location,project,startDateTuple,endDateTuple,
                                   timeZone,sensorType,condition,climate,coord]
        return PERdict
    except Exception as e:
        print e
        raise Exception("Cannot find/open 'PER Logger Data.xlsx' in the parent directory, or the file format is faulty")

def inversePERdict():
    try:
    #Open the PER Meta Data Excel spreadsheet and create a dictionary with site + location as key and
    #data logger serial as the value. Used to determine which loggers are at each site
        
        workbook = xlrd.open_workbook('.\PER Logger Data.xlsx')
        sheet = workbook.sheet_by_index(0)

        invPER = {}

        for rx in [r for r in range(sheet.nrows) if r > 1]:
            r = sheet.row(rx)
            if r[0].value!='':
                serial = r[0].value
                site = r[1].value
                location = r[2].value
                if invPER.has_key(site + location):
                    invPER[site + location].append(serial)
                else:
                    invPER[site + location] = [serial]
        return invPER
    except Exception as e:
        print e
        raise Exception("Cannot find/open 'PER Logger Data.xlsx' in the parent directory, or the file format is faulty")


def getDataObjects(sensor_protocol,PERdict):
    try:
        #Create madgetech objects from all valid .csv files in folder. create a dictionary of these objects with serial as key
        #eliminate sensors that do not have a listed gps coordinate and csv files that are not for corrosion sensors.

        #if the files in the folder are not valid madgetech2 files, attempt to convert from madgetech 4.
        #If the files are still not processable, attempt processing as hoborht logger file.
        mts = []
        hoborhts = []
        namelist = []
        for root, dirs, files in os.walk(r'.\raw'):
            namelist.extend([(root,file_) for file_ in files if file_.split('.')[1] == 'csv'])
        namelist = sorted(list(set([r+'\\'+f for r,f in namelist if not ' converted mt4' in r])))
        for name in namelist:
            mt = mt2.mt2file(name)
            if mt.valid: #Valid madgetech2 file
                mts.append(mt)
            else:
                from madgetech.madgetech_4 import mt4_to_mt2
                newpath = mt4_to_mt2(name)
                if newpath: #Valid madgetech4 file (Converted from xlsx to csv)
                    mts.append(mt2.mt2file(newpath))
                else:
                    from hobo import hoboRHT
                    hoborht = hoboRHT(name)
                    if hoborht.valid: #Valid hobo RHT logger file
                        hoborhts.append(hoborht)
                    else:
                        print 'File at %s is not a recognized data type'%name                    
                print mt.fileName + '\n'
                
        for mt in [mt for mt in mts if not mt.serial in PERdict.keys()]:
            print 'The entry for %s is missing from the "PER Logger Data.xlsx" file'%mt.serial
        print '\n'
        mts = [mt for mt in mts if mt.serial in PERdict.keys()]
        for mt in [mt for mt in mts if PERdict[mt.serial][9]!=('','')]:
            print 'The entry for %s in the "PER Logger Data.xlsx" file is missing GPS Coordinates'%mt.serial
        print '\n'
        
        mtdict = dict([(mt.serial,mt) for mt in mts if PERdict[mt.serial][9]!=('','') and PERdict[mt.serial][6]==sensor_protocol])
        keys = sorted(mtdict.keys())
        
        return mtdict, keys, hoborhts
        
    except Exception as e:
        print e
        raise Exception("Unable to convert data into data containing objects.")
