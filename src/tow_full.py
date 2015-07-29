import xlrd,csv,datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from pylab import get_cmap
from madgetech import madgetech_2 as mt2
from madgetech.madgetech_2_tow import TOWprocessor
from math import sqrt

def oldbucket(d,bucketCount):
    #currently unused bucketing method 
    dataCount = len(d)
    min_,max_ = min(d),max(d)
    Range = max_-min_
    buckets = [0 for i in range(bucketCount)]
    
    lowlim = [x*Range/float(bucketCount)+min_ for x in range(bucketCount)][::-1]
    sum_ = 0
    for i in d:
        sum_ += i
        for j in lowlim:
            if i > j:
                buckets[bucketCount-lowlim.index(j)-1] += 1
                break
    return max_,min_,dataCount,[x/float(dataCount) for x in buckets],sum_/float(dataCount*25)

bucketCount = int(raw_input('bucket count? '))
try:
    try:
    #Open the PER Meta Data excel spreadsheet and create a dictionary with serial's as the key and
    #various meta data as the value.
        workbook = xlrd.open_workbook('..\PER Logger Data.xlsx')
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
                PERdict[serial] = [site,location,project,startDateTuple,endDateTuple,
                                   timeZone,sensorType,condition,climate,coord]
    except Exception as e:
        print e
        raise Exception("Cannot find/open 'PER Logger Data.xlsx' in the parent directory, or the file format is faulty")
    
    #Create madgetech objects from all valid .csv files in folder. create a dictionary of these objects with serial as key
    #eliminate sensors that do not have a listed gps coordinate and csv files that are not for TOW sensors.
    mts = mt2.mt2folder(r'..\2 TOW Sensor Analysis\_raw')
    mtdict = dict([(mt.serial,mt) for mt in mts if PERdict[mt.serial][9]!=('','') and PERdict[mt.serial][6]=='TOW'])
    keys = sorted(mtdict.keys(),key = lambda x:PERdict[x][0])

    #create lists for the cross site Q4 plots
    overallPlotT = []
    overallQ4inc = []
    overallQ4time = []

    #create TOW data processor
    TOWproc = TOWprocessor()

    with open('TOW bucketing.csv','wb') as csvfile:
        csvwrite = csv.writer(csvfile,delimiter = ',')
        csvwrite.writerow(['Site','Location','minimun Voltage','maximum Voltage','Readings','Mean','Q1','Q2+Q3','Q4']+['Bucket ' + str(n) for n in range(bucketCount)])
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
            if mt.channelunits[0] == 'UNITVOLTS':
                data = [float(x[1])*1000 for x in data if x[0]>=startDate and x[0]<=endDate]
            else:
                data = [float(x[1]) for x in data if x[0]>=startDate and x[0]<=endDate]
            del(mt)

            tt,count,buckets,Q,Q4inc,Q4time,min_,max_,avg = TOWproc.runAnalysis(data,secondInterval,bucketCount)

            #Add the TOW aggregates to the overall list.
            overallQ4inc.append(Q4inc)
            overallQ4time.append(Q4time)
            if len(tt) > len(overallPlotT): overallPlotT = tt

            csvwrite.writerow([site,location,min_,max_,count,avg,Q['Q1']*100,Q['Q23']*100,Q['Q4']*100]+[x*100 for x in buckets])
                  
    for i in [0,1]:
        #Overall TOW plot
        #=================================================================================================

        #general chart settings
        YY = [overallQ4inc,overallQ4time][i]
        title = ['Cross Site Time of Wetness Q4','Cross Site Cumulative Time Wet'][i]
        yaxis = ['Q4','Cumulative Time Wet [D]'][i]
        
        colors = (['r','g','b','y','c','m','k']*int(len(keys)/7 + 1))[:len(keys)+1]
        overallfig, overallaxes = plt.subplots(nrows=1, ncols=1,figsize=(16,14),dpi = 100)
        overallaxes.tick_params(labelsize=14)
        overallaxes.set_title(title,fontsize = 20)
        overallaxes.set_xlabel('Exposure Time [D]',fontsize = 16)
        overallaxes.set_ylabel(yaxis,fontsize = 16)
        overallaxes.set_xlim([0,overallPlotT[-1]])
        if not i: overallaxes.set_ylim([0,0.75])

        #plot each line, and create a corresponding legend entry
        #Some convoluted indexing to get colors sorted by maximum value while maintaining proper label names
        maxCI = {}
        for ind,val in enumerate(sorted(enumerate(YY),key=lambda x:x[1][-1])):
            s = PERdict[keys[val[0]]][0]+(' Total Time Wet = ' if i else ' Final Q4 = ')+(str(val[1][-1])[:6])
            maxCI[s] = val[1][-1]
            overallaxes.plot(overallPlotT[:len(val[1])],val[1],label=s,color = colors[ind])


        #print 100% Q4 and 33.3% Q4 lines on the Time Wet graph
        if i:
            overallaxes.set_ylim(list(overallaxes.axis()[2:])) #Fix axis to avoid scaling
            overallaxes.plot([0,overallPlotT[-1]],[0,overallPlotT[-1]],'k--',label = '100% Wet (Immersion Conditions)')
            overallaxes.plot([0,overallPlotT[-1]],[0,overallPlotT[-1]/3.0],'k-.',label = '33.3% Wet (GM 9540P)')
            maxCI['100% Wet (Immersion Conditions)'],maxCI['33.3% Wet (GM 9540P)'] = overallPlotT[-1],overallPlotT[-1]/3.0

        #Shrink current axis by 20%
        #box = overallaxes.get_position()
        #overallaxes.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        
        #Create sorted legend and change legend parameters
        h,l = overallaxes.get_legend_handles_labels()
        hl = sorted(zip(h,l),key=lambda x:maxCI[x[1]],reverse=True)
        h,l = zip(*hl)
        lgd = overallaxes.legend(h,l,loc='center left',prop={'size':15+((40-len(YY))/40.)*1.5},bbox_to_anchor=(1.01, 0.5))

        #additional chart settings
        overallaxes.yaxis.set_major_locator(MaxNLocator(5))
        overallfig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=1.4)
        overallfig.tight_layout()
        overallfig.savefig(title+'.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
        #================================================================================================

    
except Exception as e:
    print e
    print "TOW sensor analysis has failed."
