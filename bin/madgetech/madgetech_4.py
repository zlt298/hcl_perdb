"""
This module is for limited conversion of Madgetech 4 files to mt2 files.
Start by opening each of your .mtff files in Madgetech 4, and export each
file to Excel without graphing. Then save each file as a .csv to a folder.
Change TARGET_FOLDER_PATH to the correct path and run this module.

This conversion will only work if each file contains data from only
one logger from one data collection period.
"""
import csv,os
import datetime as dt

def excel_date(inputdate):
    """Convert a python datetime to a Microsoft Excel 2007 floating point date"""
    temp = dt.datetime(1899, 12, 30)
    delta = inputdate - temp
    return float(delta.days) + (float(delta.seconds) / 86400)

def mt4_to_mt2(file_):
    try:
        print 'Converting: %s'%file_
        read_file = open(file_,'r')
        csvreader = csv.reader(read_file,delimiter = ',')
        data = []
        metaDict = {'"SerialNumber"':None,'"DeviceName"':None,'"StartDate"':None,'"EndDate"':None,
                    '"ReadingRate"':None,'"Readings"':None,'"TimeZone"':'"TZUTC+000000|STANDARD|UTC"',
                    '"Channels"':None}
        for ind,line in enumerate(csvreader):
            if ind == 0 : metaDict['"DeviceName"'] = '"%s"'%line[2]
            if ind == 2 : metaDict['"SerialNumber"'] = '"%s"'%line[2]
            if ind == 3 : title = line[-1] if line[-1] != '' else '%s converted'%file_.split('.')[0]
            if ind == 6 :
                column_headers = line
                metaDict['"Channels"'] = '"%i"'%(len(line)-2)
                for i,channel in enumerate(line[2:]):
                    unittype,unit = channel.split(' (')
                    unit = unit.replace(')','')
                    if unittype == 'Temperature': metaDict['"UnitType(%i)"'%i] = '"UTYPTEMPERATURE"'
                    elif unittype == 'Humidity': metaDict['"UnitType(%i)"'%i] = '"UTYPRELATIVEHUMIDITY"'
                    elif unittype == 'Bridge Output': metaDict['"UnitType(%i)"'%i] = '"UTYPVOLTAGE"'
                    elif unittype == 'Voltage': metaDict['"UnitType(%i)"'%i] = '"UTYPVOLTAGE"'
                    else: raise Exception('Unknown Unit Type')
                    if 'C' in unit: metaDict['"Unit(%i)"'%i] = '"UNITDEGREESC"'
                    elif 'RH' in unit : metaDict['"Unit(%i)"'%i] = '"UNITPERCENTRH"'
                    elif unit == 'mV': metaDict['"Unit(%i)"'%i] = '"UNITMILLIVOLTS"'
                    elif unit == 'V': metaDict['"Unit(%i)"'%i] = '"UNITVOLTS"'
                    else: raise Exception('Unknown Unit')
            if ind > 6:
                date = dt.datetime.strptime(line[0]+' '+line[1],'%m/%d/%Y %I:%M:%S %p')
                if ind == 7: metaDict['"StartDate"'] = '"%f"'%excel_date(date)
                if ind == 8:
                    dtinterval = date - prevdate
                    metaDict['"ReadingRate"'] = '"R%iS"'%dtinterval.seconds
                row = ['"%i"'%(ind-7),'"%f"'%excel_date(date)]
                for val in line[2:]:
                    row.append('"%s"'%val)
                    row.append('"0"')
                    row.append('""')
                row.append('"&B10000000"')
                row.append('"&B00000000"')
                data.append(row)
                prevdate = date
        metaDict['"EndDate"'] = '"%f"'%excel_date(date)
        metaDict['"Readings"'] = '"%i"'%(ind-6)
        read_file.close()
        
        contents = [['"%DATA MadgeTech Data File"','"This file has been converted from madgetech 4.0"']]
        for key in metaDict.keys():
            contents.append([key,metaDict[key]])
        contents.append(['"[Display]"'])
        contents.append(['"[Reading]"'])
        headers = ['# ID #','# DateTime #']
        for val in column_headers[2:]:
            headers.append('# %s #'%val)
            headers.append('# StatusByte #')
            headers.append('# Annotation #')
        headers.append('# Status #')
        headers.append('# Selections #')
        contents.append(headers)

        for row in data:
            contents.append(row)
        contents.append(['"[End Reading]"'])

        import re
        newfilepath =re.sub(r"\.(?=[^.]*$)", r" converted mt4.", file_)
        write_file = open(newfilepath,'wb')
        csvwriter = csv.writer(write_file,delimiter = ',',quotechar="'")
        for row in contents:
            csvwriter.writerow(row)
        write_file.close()
        return newfilepath
        
    except Exception as e:
        print e
        print file_, ' Failed to convert'
        return False
    print '\n'
