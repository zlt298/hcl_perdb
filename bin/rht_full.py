import xlrd,csv,datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
from pylab import get_cmap
from madgetech import madgetech_2 as mt2
from madgetech.madgetech_2_rht import rhtProcessor
from perdb import perdb
from math import sqrt

try:
    #load meta data into a dictionary
    PERdict = perdb.loadPERdict()
    invPERdict = perdb.inversePERdict()
    
    #Create madgetech objects from all valid .csv files in folder. create a dictionary of these objects with serial as key
    #eliminate sensors that do not have a listed gps coordinate and csv files that are not for corrosion sensors.
    mts = mt2.mt2folder(r'..\3 RHT and TC Sensor Analysis\_raw')
    mtdict = dict([(mt.serial,mt) for mt in mts if PERdict[mt.serial][6]=='RHT'])
    keys = sorted(mtdict.keys())

    #create rht data processor
    rhtproc = rhtProcessor()

    tempAggregates = []
    rhAggregates = []

    for key in keys:
        mt = mtdict[key]
        mt.loaddata()
        secondInterval = mt.timeinterval.total_seconds()
        site,location,project,startDateTuple,endDateTuple,timeZone,sensorType,condition,climate,coord = PERdict[key]
        
        startDate = (datetime.datetime(*startDateTuple)+datetime.timedelta(hours = 24)).strftime('%Y/%m/%d %H:%M:%S')
        endDate = (datetime.datetime(*endDateTuple)-datetime.timedelta(hours = 24)).strftime('%Y/%m/%d %H:%M:%S')
        print site
        print "Start Date, End Date:"
        print startDate,endDate
        data = mt.getData() #('%Y/%m/%d %H:%M:%S',value)
        del(mt)

        tt,T,rh = rhtproc.format_dat(data,secondInterval)
        #T = rhtproc.cut_bounds(T,[-5,45])
        #rh = rhtproc.cut_bounds(rh,[0,100])

        #Plot enveloped temp and rh data
        titles = ['Ambient Temperature','Relative Humidity']
        units = ['Temperature [$^\circ$C]','Relative Humidity [%]']
        dat = [np.array(T),np.array(rh)]
        
        for i in [0,1]:
            fig, axes = plt.subplots(nrows=1, ncols=1,figsize=(16,6),dpi = 100)
            axes.tick_params(labelsize=14)
            axes.set_title(titles[i],fontsize = 20)
            axes.set_xlabel('Exposure Time [D]',fontsize = 16)
            axes.set_ylabel(units[i],fontsize = 16)
            axes.set_xlim([0,tt[-1]])
            rhtproc.envelope_plot(np.array(tt), dat[i], winsize=48, ax=axes)
            axes.yaxis.set_major_locator(MaxNLocator(5))
            fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=1.4)
            fig.suptitle(site,fontsize = 16,horizontalalignment='right',
                         verticalalignment='top',x = 1,y = 1)
            fig.tight_layout()
            fig.savefig(site+ ' ' + titles[i]+' Enveloped Graph.png')
            fig.clf()
        
        #plot temp and rh data
        for i in [0,1]:
            fig, axes = plt.subplots(nrows=1, ncols=1,figsize=(16,6),dpi = 100)
            axes.tick_params(labelsize=14)
            axes.set_title(titles[i],fontsize = 20)
            axes.set_xlabel('Exposure Time [D]',fontsize = 16)
            axes.set_ylabel(units[i],fontsize = 16)
            axes.set_xlim([0,tt[-1]])
            plt.plot(np.array(tt), dat[i])
            axes.yaxis.set_major_locator(MaxNLocator(5))
            fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=1.4)
            fig.suptitle(site,fontsize = 16,horizontalalignment='right',
                         verticalalignment='top',x = 1,y = 1)
            fig.tight_layout()
            fig.savefig(site+ ' ' + titles[i]+' Graph.png')
            fig.clf()
                
        min_,max_,avg = min(T),max(T),sum(T)/float(len(T))
        tempAggregates.append((min_,max_,avg))
        
        min_,max_,avg = min(rh),max(rh),sum(rh)/float(len(rh))
        rhAggregates.append((min_,max_,avg))
    
    print tempAggregates
    print rhAggregates
   

    
except Exception as e:
    print e
    print "rht sensor analysis has failed."
