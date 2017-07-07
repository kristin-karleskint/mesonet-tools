#### mitchell sawtelle 7/4/2017
#### mitchell.sawtelle@okstate.edu

import datetime #import datetime module to get. this module manipulates dates.
import os #import os deals with filesystem operations such as making folders
from urllib.request import Request,urlopen #import urllib.request which allows us to access the web
from random import uniform #uniform generates float between given 2 values
import time #import time to use time.sleep() which can delay the execution of code for the specified number of secs
from matplotlib import pyplot as plt
import calendar
class PyMesonet(object):
    def __init__(self,raingauge,destination=None):
        super(PyMesonet, self).__init__()
        # raingauge is the abbreviation for a mesonet raingauge entered as string ex.  'okcn'
        # destination is the path to the desired directory for the mesonet data to be stored in
        # destination defualts to None and if no destination value is given in __init__() use cwd
        if destination is None: self.destination = os.path.dirname(__file__)
        else: self.destination = destination
        self.baseurl = 'https://www.mesonet.org/index.php/dataMdfMts/dataController/getFile/{0:4d}{1:02d}{2:02d}{3}/mts/TEXT/'#baseurl pattern for mesonet files
        self.currentpath = os.path.dirname(__file__)#cwd
        self.raingauge = raingauge # raingauge is the abbreviation for a mesonet raingauge entered as string ex.  'okcn'
        self.defaultfolder = os.path.join(self.destination,'{}{}'.format(self.raingauge,'-raindata')) #path to new folder in cwd named the given rainguauge-raindata ex okcn-raindata
        self.rainfilename = [self.raingauge,'raindata','5min',0]




    def download(self, d1, d2=None):
        # a function to download mesonet rain data from the web and write to .dat files
        # files from the mesonet are in UTC time so data for ex. 2017-07-04 is from 7:00:00PM CDT 2017-07-03 to 6:55:00PM CDT 2017-07-04
        # d1 is the older date must be entered as a list, [year,month,day], or tuple, (year,month,day)

        # **kwarg d2 is the optional newer date must be entered as a list, [year,month,day], or tuple, (year,month,day)
        ## if d2 is not specified the downloader will only download the data for d1
        ### if d2 is given then the downloader will get all the days between d2 and d1 inclusively

        d1 = datetime.date(*d1) #*d1 means unpack the list or tuple that is given in the mesonetdownload function and use them as inputs in the class date(year,month,day)
        dates = [] #list to store all dates between d1 and d2
        last = 0
        y = self.rainfilename
        if not os.path.exists(self.defaultfolder):#make default folder in cwd if it does not already exist else pass
            os.mkdir(self.defaultfolder)
        else:
            pass
        output = self.defaultfolder

        if d2 is not None:
            #for loop to get all the dates between d2 and d1
            #timedelta is a class which expresses duration ex. 4 days
            #for the number of days bettwen d2 and d1 ex. 51 days set i = 0 through 51
            #d1 + timedelta will give a date ex. 2017-07-04
            #append all the dates between d2 and d1 to the dates list to be used later to download all the files at once using a for loop
            d2 = datetime.date(*d2)
            delta = d2 - d1 #number of days between d2 and d1

            for i in range(delta.days + 1):

                dates.append(d1 + datetime.timedelta(days=i))

            print('{}{}{}'.format('there are ',len(dates),' days between d2 and d1'))
            print('starting downloads')

            for d in dates: #for loop to gather data from mesonet for each date in the dates list
                y[3]=d
                last = 0
                time.sleep(uniform(1,2)) #pause the code for 1 or 2 sec.
                year, month, day = d.year, d.month, d.day #passing year, month, and day attributes from the date class to respective variables year,month, day
                fileoutput = '{3}-{0}-{1}-{2}.dat'.format(*y)#names of the each file for current date
                if os.path.exists(os.path.join(output,fileoutput)):
                    print('file for '+ str(d) + ' already exists moving on to the next day')
                    continue
                lines = ['{} 19:00:00PM 0.00\n'] #list to store reformatted timestamps to ex. 1994/10/19 02:05:00AM 0.0 for SWMM
                dateformat = '{:04d}/{:02d}/{:02d}' #format date from current date
                rainlist = [] #list to store rain data
                accessurl = self.baseurl.format(year,month,day,self.raingauge) #create url to download data from mesonet using .format
                req = Request(accessurl) #request object of accessurl
                link = urlopen(req) #open request object
                raindata = link.read().decode() #decode string from website
                rows = raindata.split('\n') #split string by newline character
                print('{}{}{}'.format('mesonet data for ', d, ' has been downloaded'))

                for row in rows[4:-1]: #iterate over rows which contain data
                    rain = float(row.split()[11]) #raindata value from row. measurement has units millimeters
                    rainlist.append(rain) #add data to rain list

                for i,data in enumerate(rainlist): #iterate over rainlist using enumerate which returns tuples (position in list, value) ex. (27th item, 2.5in)
                    dif = data - last #calculate difference between raindata of the current time period and the previous since values are give as cumulutive instead of difference
                    last = data
                    t = (i+1)*5 #multiply the position in rainlist by five to get the time intervals of 5 mins
                    h = t//60 #get current time period hour values using floor divsion
                    m = t%60 #get current time period min value by dividing by 60 and getting using remainder
                    s = 0 #seconds value is always 0
                    h+=19 #24hr time
                    if t < 300: #first 5 hrs
                        period = 'PM'
                        basetime = '{0:02d}:{1:02d}:{2:02d}{3:}'.format(h,m,s,period)#use format to set time stamp using current values
                        prevday = day - 1 #first five hours are from previous calendar day

                        if prevday == 0: #if the date entered was the first of the month get the correct previous day
                            if month == 1: #if the input is the first day of the year go back to pervious year 31st of December
                                prevyear = year - 1
                                prevmonth = 12
                                prevday = 31
                                lines[0]=lines[0].format(dateformat.format(prevyear, prevmonth, prevday))
                                line = '{} {} {:.2f}\n'.format(dateformat.format(prevyear,prevmonth,prevday),basetime,dif)
                            else: #else just go back one month
                                prevmonth = month - 1
                                dayrange = calendar.monthrange(year,prevmonth)#get the last day of the prevmonth
                                prevday = dayrange[1]#last day of prev month
                                lines[0] = lines[0].format(dateformat.format(year, prevmonth, prevday))
                                line = '{} {} {:.2f}\n'.format(dateformat.format(year, prevmonth, prevday), basetime, dif)

                        else:
                            lines[0] =lines[0].format(dateformat.format(year,month,day-1))#else not first of the month just go back one day
                            line = '{} {} {:.2f}\n'.format(dateformat.format(year, month, prevday), basetime, dif)
                    elif 300 <= t < 1020:
                        period = 'AM'
                        h-=24
                        basetime = '{0:02d}:{1:02d}:{2:02d}{3:}'.format(h,m,s,period) #use format to set time stamp using current values
                        line = '{} {} {:.2f}\n'.format(dateformat.format(year,month,day),basetime,dif)
                    else:
                        period = 'PM'
                        h-=24
                        basetime = '{0:02d}:{1:02d}:{2:02d}{3:}'.format(h,m,s,period) #use format to set time stamp using current values
                        line = '{} {} {:.2f}\n'.format(dateformat.format(year,month,day),basetime,dif)

                    lines.append(line) #add line to list of lines
                with open(r'{}\{}'.format(output,fileoutput),'w') as f: #mkae files for each date write all timestamps to files
                    print('file for {} has been completed'.format(d))
                    f.writelines(lines)
        else:
            print('only d1 given gathering data for {} at station {}'.format(d1,self.raingauge))
            year, month, day = d1.year, d1.month, d1.day
            dateformat = '{:04d}/{:02d}/{:02d}' #format date from current date
            last = 0
            y[3] = d1
            fileoutput = '{3}-{0}-{1}-{2}.dat'.format(*y)#names of the each file for current date
            lines = ['{} 19:00:00PM 0.00\n']  #list to store reformatted timestamps to ex. 1994/10/19 02:05:00AM 0.0 for SWMM
            rainlist = [] #list to store rain data
            if os.path.exists(os.path.join(output,fileoutput)):
                print('file for '+ str(d1) + ' already exists delete file manually if you wish to download new version for ' + str(d1))
                return
            accessurl = self.baseurl.format(year,month,day,self.raingauge) #create url to download data from mesonet using .format
            req = Request(accessurl) #request object of accessurl
            link = urlopen(req) #open request object
            raindata = link.read().decode() #decode string from website
            rows = raindata.split('\n') #split string by newline character
            print('{}{}{}'.format('mesonet data for ', d1, ' has been downloaded'))

            for row in rows[4:-1]: #iterate over rows which contain data
                rain = float(row.split()[11]) #raindata value from row. measurement has units millimeters
                rainlist.append(rain) #add data to rain list

            for i,data in enumerate(rainlist): #iterate over rainlist using enumerate which returns tuples (position in list, value) ex. (27th item, 2.5in)
                dif = data - last #calculate difference between raindata of the current time period and the previous since values are give as cumulutive instead of difference
                last = data #replace previous time period raindata value with the current time period value
                t = (i+1)*5 #multiply the position in rainlist by five to get the time intervals of 5 mins
                h = t//60 #get current time period hour values using floor divsion
                m = t%60 #get current time period min value by dividing by 60 and getting using remainder
                s = 0 #seconds value is always 0
                h+=19 #put hours into 24hr time
                if t < 300:# see lines 94-130 for comment
                    period = 'PM'
                    basetime = '{0:02d}:{1:02d}:{2:02d}{3:}'.format(h,m,s,period)#use format to set time stamp using current values
                    prevday = day - 1

                    if prevday == 0:
                        if month == 1:
                            prevyear = year - 1
                            prevmonth = 12
                            prevday = 31
                            lines[0]=lines[0].format(dateformat.format(prevyear, prevmonth, prevday))
                            line = '{} {} {:.2f}\n'.format(dateformat.format(prevyear,prevmonth,prevday),basetime,dif)
                        else:
                            prevmonth = month - 1
                            dayrange = calendar.monthrange(year,prevmonth)
                            prevday = dayrange[1]
                            lines[0] = lines[0].format(dateformat.format(year, prevmonth, prevday))
                            line = '{} {} {:.2f}\n'.format(dateformat.format(year, prevmonth, prevday), basetime, dif)

                    else:
                        lines[0] =lines[0].format(dateformat.format(year,month,day-1))
                        line = '{} {} {:.2f}\n'.format(dateformat.format(year, month, prevday), basetime, dif)

                elif 300 <= t < 1020:
                    period = 'AM'
                    h-=24
                    basetime = '{0:02d}:{1:02d}:{2:02d}{3:}'.format(h,m,s,period) #use format to set time stamp using current values
                    line = '{} {} {:.2f}\n'.format(dateformat.format(year,month,day),basetime,dif)
                else:
                    period = 'PM'
                    h-=24
                    basetime = '{0:02d}:{1:02d}:{2:02d}{3:}'.format(h,m,s,period) #use format to set time stamp using current values
                    line = '{} {} {:.2f}\n'.format(dateformat.format(year,month,day),basetime,dif)

                lines.append(line) #add line to list of lines
            with open(r'{}\{}'.format(output,fileoutput),'w') as f: #mkae files for each date write all timestamps to files
                print('file for {} has been completed'.format(d1))
                f.writelines(lines)

    def daytotal(self, d1, d2=None):
        # function to total raindata for specified date or dates
        # files from the mesonet are in UTC time so data for ex. 2017-07-04 is from 7:00:00PM CDT 2017-07-03 to 6:55:00PM CDT 2017-07-04
        # d1 is the older date must be entered as a list, [year,month,day], or tuple, (year,month,day)
        # **kwarg d2 is the optional newer date must be entered as a list, [year,month,day], or tuple, (year,month,day)
        # if d2 is not specified the downloader will only download the data for d1
        # if d2 is given then the downloader will get all the days between d2 and d1 inclusively



        d = datetime.date(*d1)
        y = self.rainfilename
        last = 0
        year, month, day = d.year, d.month, d.day
        prevday = day - 1
        total = 0

        if prevday == 0:
            if month == 1:
                prevyear = year - 1
                prevmonth = 12
                prevday = 31
                prevdate = datetime.date(prevyear,prevmonth,prevday)
            else:
                prevmonth = month - 1
                dayrange = calendar.monthrange(year,prevmonth)
                prevday = dayrange[1]
                prevdate = datetime.date(year,prevmonth,prevday)
        else:
            prevdate = datetime.date(year,month,prevday)

        y[3] = d
        fileoutput = '{3}-{0}-{1}-{2}.dat'.format(*y)
        print(fileoutput)
        y[3] = prevdate
        pfileoutput = '{3}-{0}-{1}-{2}.dat'.format(*y)
        print(pfileoutput)

        if os.path.exists(os.path.join(self.defaultfolder,pfileoutput)):
            rainfile = os.path.join(self.defaultfolder,pfileoutput)
            with open(rainfile,'r') as f:
                content = f.read()
                rows = content.split('\n')
                for row in rows[60:287]:
                    raindata = row.split()[-1]
                    raindata = float(raindata)
                    total = total + raindata

        else:
            self.download((prevdate.year,prevdate.month,prevdate.day))
            rainfile = os.path.join((self.defaultfolder,pfileoutput))
            with open(rainfile,'r') as f:
                content = f.read()
                rows = content.split('\n')
                for row in rows[60:287]:
                    raindata = row.split()[-1]
                    raindata = float(raindata)
                    total = total + raindata

        if os.path.exists(os.path.join(self.defaultfolder,fileoutput)):
            rainfile = os.path.join(self.defaultfolder,fileoutput)
            with open(rainfile,'r') as f:
                content = f.read()
                rows = content.split('\n')
                for row in rows[:59]:
                    raindata = row.split()[-1]
                    raindata = float(raindata)
                    total = total + raindata
        else:
            self.download([year,month,day])
            rainfile = os.path.join((self.defaultfolder,fileoutput))
            with open(rainfile,'r') as f:
                content = f.read()
                rows = content.split('\n')
                for row in rows[:59]:
                    raindata = row.split()[-1]
                    raindata = float(raindata)
                    total = total + raindata
        print(total)
        return total
