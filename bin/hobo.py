import os
import csv
import datetime


class hoboRHT:
    """
    The hoboRHT object is for easy manipulation of hobo RHT data files in the
    '.csv' format. 
    filePath is the string of the file path to the desired .csv file
    """
    def __init__(self,filePath):
        self.valid = True
        self.filePath = filePath
        self.fileName = None
        self.file = None
        
        #metadata variables
        self.serial = None          #Logger Serial Number as string
        self.startdate = None       #First Entered time as datetime object
        self.enddate = None         #Last Entered time as datetime object
        self.timeinterval = None    #Time interval in seconds between measurements as float
        self.readings = None        #Number of measurements taken as integer
        self.timezonedelta = None   #Hours from GMT as +- integer
        self.channels = []          #Headers for each data column
        self.channelunits = []      #Units for each data column
        
        #data variables; data is a not a dictionary as channel headers can be non-unique
        self.data = []

        #Open the file at filePath, and load the meta data and data
        try:
            if os.path.isfile(filePath):
                self.file = open(self.filePath,'rb')
                
                csvread = csv.reader(self.file,delimiter = ',')
                for ind,line in enumerate(csvread):
                    ##Meta data Processing++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    if ind == 0: #File name
                        self.fileName = line[0].split(': ')[-1].split('"')[0]
                        print 'Started processing %s...'%self.fileName
                    elif ind == 1: #Meta Data
                        self.serial = line[2].split('S/N: ')[1].split(',')[0]
                        self.timezonedelta = int(line[1].split('GMT')[1].split(':')[0])

                        #Channel and channel units
                        self.channels.extend(['Index','Datetime'])
                        self.channelunits.extend(['#','mm/dd/yy HH:MM:SS'])
                        for c in line[1:]:
                            if 'SEN S/N:' in c:
                                self.channels.append(c.split('(')[0].split(',')[0].strip())
                            if ',' in c:
                                self.channelunits.append(c.split(' (')[0].split(', ')[-1].replace('\xc2',''))
                            if 'GMT' in c:
                                self.channelunits.pop()
                    elif ind == 2: #First line of data
                        self.startdate = datetime.datetime.strptime(line[1],'%m/%d/%y %I:%M:%S %p')
                        self.readings = 1
                    else:
                        if line[2] != '':
                            if self.timeinterval == None:
                                tempdate = datetime.datetime.strptime(line[1],'%m/%d/%y %I:%M:%S %p')
                                self.timeinterval = tempdate - self.startdate
                                self.timeinterval = self.timeinterval.total_seconds()
                                print self.timeinterval
                            self.readings += 1
                    ##Meta data Processing++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

                    ##Data Processing=========================================================================
                    if ind > 1 and line[2] != '':
                        row = []
                        row.append(self.readings)
                        tempdate = datetime.datetime.strptime(line[1],'%m/%d/%y %I:%M:%S %p')
                        dt = tempdate.strftime('%m/%d/%y %H:%M:%S')
                        row.append(dt)
                        for c in [x for x in line[2:] if x != '']:
                            row.append(float(c))
                        self.data.append(row)
                        
                    ##Data Processing=========================================================================
                self.enddate = tempdate
            else:
                raise Exception('Input file path is invalid')
        except Exception as e:
            self.valid = False
            print e
            print filePath + ' Does not lead to a valid hobo RHT data file.'

    def imp2metric(self):
        self.channelunits = [x.replace('F','C') for x in self.channelunits]
        for ind in xrange(self.readings):
            self.data[ind][2] = (self.data[ind][2]-32.)/1.8
            self.data[ind][4] = (self.data[ind][4]-32.)/1.8

    def plotDat(self,enveloped = False):
        return None

    

if __name__ == '__main__':
    rhtp0 = hoboRHT('.\HOBO_P0.csv')
    print rhtp0.channels
    print rhtp0.channelunits
    for r in rhtp0.data[0:10]:
        print r
    print '\n\n\n'
    rhtp0.imp2metric()
    print rhtp0.channels
    print rhtp0.channelunits
    for r in rhtp0.data[0:10]:
        print r
    print '\n\n\n'
    
