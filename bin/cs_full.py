import xlrd,csv,datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from pylab import get_cmap
from googleEarth import plotGoogleColorMap as pltGE
from perdb import perdb
from madgetech import madgetech_2 as mt2
from madgetech.madgetech_2_cs import CorrosionSensorProcessor

try:
    #load meta data into a dictionary
    PERdict = perdb.loadPERdict()
    invPERdict = perdb.inversePERdict()
    
    #Create madgetech objects from all valid .csv files in folder. create a dictionary of these objects with serial as key
    #eliminate sensors that do not have a listed gps coordinate and csv files that are not for corrosion sensors.
    mts = mt2.mt2folder(r'..\1 Corrosion Sensor Analysis\_raw')
    mtdict = dict([(mt.serial,mt) for mt in mts if PERdict[mt.serial][9]!=('','') and PERdict[mt.serial][6]=='CS'])
    keys = sorted(mtdict.keys())

    #create lists for the cross site cumulative corrosion index and the Google Earth color plot
    overallPlotT=[]
    overallPlotY = []
    googleEarthList = []
    
    #create a corrosion sensor data processing object (Contains functions for processing corrosion sensor data)
    csProc = CorrosionSensorProcessor(useDefaultInput = True)
    
    #Iterate through serial numbers
    for key in keys:
        try:
            #load data from the mt object and truncate data to the dates listed in the PER meta data excel spreadsheet
            #If the data is in millivolts, convert to volts before stripping the date column of the data, otherwise
            #proceed with stripping the date column
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
            if mt.channelunits[0] == 'UNITMILLIVOLTS':
                data = [float(x[1])/1000 for x in data if x[0]>=startDate and x[0]<=endDate]
            else:
                data = [float(x[1]) for x in data if x[0]>=startDate and x[0]<=endDate]
            del(mt)

            #Run the corrosion sensor analysis
            tt,wet,wetP,wetT,dry,dryP,dryT,cyc,chl,ic,cci = csProc.runAnalysis(data,secondInterval,*csProc.ANALYSIS_INPUT)
            googleEarthList.append((coord,cci[-1],location))

            #Plot the data, wetstring, dry string, chloride equivalent, incremental corrosion and cumulative corrosion index
            csProc.plotAnalysis(site,data,tt,wet,dry,chl,ic,cci)

            #Save various aggregates into a csv file (similar to the overview in the A-D per binder)
            csProc.csvAnalysis(site,tt,wet,wetP,wetT,dry,dryP,dryT,cyc,chl,ic,cci)

            #add the cumulative corrosion index data to the overall list.
            overallPlotY.append(cci)
            if len(tt) > len(overallPlotT): overallPlotT = tt
            
        except Exception as e:
            print e
            print "Something went wrong with the data processing for "+site+" ... Skipping ..."
            continue

    try:
        #Overall corrosion index plot
        #=================================================================================================
        #general chart settings
        colors = (['r','g','b','y','c','m','k']*int(len(keys)/7 + 1))[:len(keys)+1]
        overallfig, overallaxes = plt.subplots(nrows=1, ncols=1,figsize=(16,12),dpi = 100)
        overallaxes.tick_params(labelsize=14)
        overallaxes.set_title('Cumulative Corrosion Index',fontsize = 20)
        overallaxes.set_xlabel('Exposure Time [D]',fontsize = 16)
        overallaxes.set_ylabel('Cumulative Corrosion Index',fontsize = 16)
        overallaxes.set_xlim([0,overallPlotT[-1]])

        #plot each line, and create a corresponding legend entry
        maxCI = {}
        for i,j in enumerate(overallPlotY):
            s = PERdict[keys[i]][0]+' Final Index = '+str(j[-1])
            maxCI[s] = j[-1]
            overallaxes.plot(overallPlotT[:len(j)],j,label=s,color = colors[i])

        #Create sorted legend and change legend parameters
        h,l = overallaxes.get_legend_handles_labels()
        hl = sorted(zip(h,l),key=lambda x:maxCI[x[1]],reverse=True)
        h,l = zip(*hl)
        overallaxes.legend(h,l,loc='upper left',prop={'size':12})

        #additional chart settings
        overallaxes.yaxis.set_major_locator(MaxNLocator(5))
        overallfig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=1.4)
        overallfig.tight_layout()
        overallfig.savefig('Cross Site Corrosion Index.png')
        #================================================================================================
    except Exception as e:
        print e
        print 'Unable to plot cross site corrosion index'
        pass

    #Create csv file for cross site corrosion index data
    try:
        #Overall corrosion index data table
        #=================================================================================================
        #Rearrange the jagged array into a tuple-list where empty data is represented by ''
        csvlist = []
        csvlist.append(['Elapsed Time [D]']+[PERdict[keys[i]][0] + ' Corrosion Index' for i in range(len(overallPlotY))])
        
        for ind,val in enumerate(overallPlotT):
            templist = [str(val)]
            for yy in overallPlotY:
                try:
                    templist.append(str(yy[ind]))
                except IndexError:
                    templist.append('')
            csvlist.append(templist)
        
        #write the newly created list to csv
        with open('Cross Site Corrosion Index Table.csv','w+b') as csvfile:
            cw = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_NONE)
            for line in csvlist:
                cw.writerow(line)
        #================================================================================================
    except Exception as e:
        print e
        print 'Unable to create csv for cross site corroison index'
        pass

    #Create google earth color map of corrosion index
    try:
        pltGE('Cumulative Corrosion',*zip(*googleEarthList))
    except Exception as e:
        print e
        print 'Unable to create google earth .kml'
        pass


except Exception as e:
    print e
    print "Corrosion sensor analysis has failed."
