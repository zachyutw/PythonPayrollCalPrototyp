
import time
from time import gmtime, strftime
import datetime

MAX_WEEKLY_WORK_HOURS=40
MAX_REGULAR_WORKHOUR=8
MAX_OVERTIMESTAGE1=12

'''
# odoo 10.0 timeformat
class TimeFormat:
    def __init__(self,YYYY,mm,dd,HH,MM,SS):
        self.YYYY=YYYY
        self.mm=mm
        self.dd=dd
        self.HH=HH
        self.MM=MM
        self.SS=SS
    def toString(self):
        return self.YYYY+'-'+self.mm+'-'+self.dd+' '+self.HH+':'+self.MM+':'+self.SS
'''


class Attendance_datetime:
    def __init__(self, check_in, check_out, worked_hours):
        self.check_in = check_in
        self.check_out = check_out
        self.worked_hours = worked_hours
        self._get_check_in_datetime()
        self._get_check_out_datetime()

    # transfer string time to datetime
    def _get_check_in_datetime(self):
        self.check_in=datetime.datetime.strptime(self.check_in, '%Y-%m-%d %H:%M:%S')

    def _get_check_out_datetime(self):
        self.check_out=datetime.datetime.strptime(self.check_out, '%Y-%m-%d %H:%M:%S')

class Attendance:
    def __init__(self,check_in,check_out,worked_hours):
        self.check_in = check_in
        self.check_out = check_out
        self.worked_hours = worked_hours

#simulate demo data attendance_ids from odoo
attendance_ids = []
attendance_ids.append(Attendance('2013-01-12 08:26:24','2013-01-12 20:26:24',20-8))
attendance_ids.append(Attendance('2014-01-12 08:26:24','2014-01-12 20:26:24',20-8))
attendance_ids.append(Attendance('2014-01-13 08:26:24','2014-01-13 10:26:24',20-8))
attendance_ids.append(Attendance('2014-01-13 12:26:24','2014-01-13 13:26:24',13-12))
attendance_ids.append(Attendance('2014-01-13 14:26:24','2014-01-13 20:26:24',20-14))
attendance_ids.append(Attendance('2015-01-12 08:26:24','2015-01-12 20:26:24',20-8))
attendance_ids.append(Attendance('2015-01-13 08:26:24','2015-01-13 20:26:24',20-8))
attendance_ids.append(Attendance('2015-01-14 08:26:24','2015-01-14 20:26:24',20-8))
attendance_ids.append(Attendance('2015-01-15 08:26:24','2015-01-15 20:26:24',20-8))
attendance_ids.append(Attendance('2015-01-16 06:26:24','2015-01-16 22:26:24',22-6))
attendance_ids.append(Attendance('2015-01-17 06:26:24','2015-01-17 22:26:24',22-6))
attendance_ids.append(Attendance('2016-01-18 03:26:24','2016-01-18 10:26:24',10-3))
attendance_ids.append(Attendance('2016-01-18 12:26:24','2016-01-18 14:26:24',14-12))
attendance_ids.append(Attendance('2016-01-18 16:26:24','2016-01-18 20:26:24',20-16))
attendance_ids.append(Attendance('2016-01-18 21:26:24','2016-01-18 23:26:24',23-21))
attendance_ids.append(Attendance('2017-01-12 08:26:24','2017-01-12 20:26:24',20-8))
attendance_ids.append(Attendance('2017-01-13 02:26:24','2017-01-13 23:26:24',23-2))
attendance_ids.append(Attendance('2017-01-14 02:26:24','2017-01-14 23:26:24',23-2))
attendance_ids.append(Attendance('2017-01-15 02:26:24','2017-01-15 23:26:24',23-2))
attendance_ids.append(Attendance('2017-01-11 02:26:24','2017-01-11 23:26:24',23-2))
attendance_ids.append(Attendance('2017-01-10 02:26:24','2017-01-10 23:26:24',23-2))
attendance_ids.append(Attendance('2017-01-09 02:26:24','2017-01-09 23:26:24',23-2))



#The class which define the work hours hr need
class DailyAttendance:
    def __init__(self,dailyHours,overtime1,overtime2,week_number,record_date,approval=False):
        self.daily_hours=dailyHours
        self.regular_hours=0
        self.overtime1=overtime1
        self.overtime2=overtime2
        self.week_number=week_number
        self.record_date=record_date
        self.approval= approval

#calculation function
class WorkingHours:
    def __init__(self,attendance_ids):
        self.weekly_hours= 0.0 #save total weekly hours = weekly overtime + weekly regular time
        self.weekly_overtime= 0.0 #save weekly overtime
        self.weekly_regular_hours=0.0 #save weekly regular time
        self.approval= False
        self.daily_working_records = [] #daily_working data
        self.attendance_ids = attendance_ids #attedance data
        self._get_weekly_worked_hour()
        self._attendance_ids_daily_working_hours()


    def attendance_ids_transfer(self):
        new_attendance_ids = []
        for att in self.attendance_ids:
            new_attendance_ids.append(Attendance_datetime(att.check_in,att.check_out,att.worked_hours))
        return new_attendance_ids

    def _attendance_ids_daily_working_hours(self):
        new_attendance_ids = self.attendance_ids_transfer()
        new_attendance_ids.sort(key=lambda r:r.check_in.date())
        i=0
        for attendance in new_attendance_ids:
            if (i == 0):
                record_date = attendance.check_in.date()
                daily_working_hours = attendance.worked_hours
                overtime1 = self.check_overtime(daily_working_hours, MAX_REGULAR_WORKHOUR)
                overtime2 = self.check_overtime(daily_working_hours, MAX_OVERTIMESTAGE1)
                week_number = attendance.check_out.strftime("%Y%V")
                self.daily_working_records.append(DailyAttendance(daily_working_hours, overtime1, overtime2, week_number,
                                                       record_date))
                if daily_working_hours > MAX_REGULAR_WORKHOUR:
                    self.daily_working_records[-1].regular_hours = MAX_REGULAR_WORKHOUR
                else:
                    self.daily_working_records[-1].regular_hours = daily_working_hours
                #print('first')
            elif (new_attendance_ids[i-1].check_in.date() == attendance.check_in.date()):
                self.daily_working_records[-1].daily_hours += attendance.worked_hours
                self.daily_working_records[-1].overtime1= self.check_overtime(self.daily_working_records[-1].daily_hours, MAX_REGULAR_WORKHOUR)
                self.daily_working_records[-1].overtime2 = self.check_overtime(self.daily_working_records[-1].daily_hours,
                                                     MAX_OVERTIMESTAGE1)
                self.daily_working_records[-1].overtime1= self.daily_working_records[-1].overtime1 - self.daily_working_records[-1].overtime2
                #leng = len(self.daily_working_records)
                #print(leng)
                if self.daily_working_records[-1].daily_hours > MAX_REGULAR_WORKHOUR:
                    self.daily_working_records[-1].regular_hours = MAX_REGULAR_WORKHOUR
                else:
                    self.daily_working_records[-1].regular_hours = self.daily_working_records[-1].daily_hours
            elif (attendance.worked_hours):
                record_date = attendance.check_in.date()
                daily_working_hours = attendance.worked_hours
                overtime1 = self.check_overtime(daily_working_hours, MAX_REGULAR_WORKHOUR)
                overtime2 = self.check_overtime(daily_working_hours, MAX_OVERTIMESTAGE1)
                overtime1 = overtime1-overtime2
                week_number = attendance.check_out.strftime("%Y%V")
                self.daily_working_records.append(DailyAttendance(daily_working_hours, overtime1, overtime2, week_number,
                                                       record_date))
                if daily_working_hours > MAX_REGULAR_WORKHOUR:
                    self.daily_working_records[-1].regular_hours = MAX_REGULAR_WORKHOUR
                else:
                    self.daily_working_records[-1].regular_hours = daily_working_hours
                #print("success")
            else:
                print("error data")
            i+=1
        self._cal_weekly_overtime()
        #self.daily_working_records.sort(key=lambda r:r.record_date)

    def check_overtime(self,hours,max_time):
        if hours > max_time:
            return hours - max_time
        else:
            return 0

    def _cal_weekly_overtime(self):
        hour = self._get_weekly_worked_hour()
        hours = hour[-1]
        if(hours> MAX_WEEKLY_WORK_HOURS):
            self.weekly_regular_hours = MAX_WEEKLY_WORK_HOURS
            self.weekly_overtime = hours - MAX_WEEKLY_WORK_HOURS
            return hours - MAX_WEEKLY_WORK_HOURS
        else:
            self.weekly_regular_hours = hours
            return hours

    def get_today_regular_hours(self):
        return 0

    def _get_weekly_worked_hour(self):
        i=0
        WH=0
        week_records=[]
        for dwr in self.daily_working_records:
            if i==0:
                WH = dwr.regular_hours
            elif (self.daily_working_records[i-1].week_number == dwr.week_number):
                WH +=dwr.regular_hours
            else:
                week_records.append(WH)
                WH = dwr.regular_hours
            i+=1
        #add last one
        week_records.append(WH)

        return week_records

    def get_total_regular_hours(self):
        total_regular_hours = 0
        if len(self.daily_working_records)>1:
            last_week_num = self.daily_working_records[-1].week_number
        else:
            last_week_num = -1
        for dwr in self.daily_working_records:
            if dwr.week_number == last_week_num:
                total_regular_hours += dwr.regular_hours
        return total_regular_hours

    def get_total_overtime1(self):
        total_overtime1 = 0
        if len(self.daily_working_records)>1:
            last_week_num = self.daily_working_records[-1].week_number
        else:
            last_week_num = -1
        for dwr in self.daily_working_records:
            if dwr.week_number == last_week_num:
                total_overtime1 += dwr.overtime1
        return total_overtime1


    def get_total_overtime2(self):
        total_overtime2 = 0
        if len(self.daily_working_records) > 1:
            last_week_num = self.daily_working_records[-1].week_number
        else:
            last_week_num = -1
        for dwr in self.daily_working_records:
            if dwr.week_number == last_week_num:
                total_overtime2 += dwr.overtime2
        return total_overtime2

workingHours=WorkingHours(attendance_ids)
#workingHours._cal_weekly_overtime()



for dwr in workingHours.daily_working_records:
    print(dwr.week_number)
    print(dwr.record_date)
    print(dwr.daily_hours)
    print(dwr.regular_hours)
    print(dwr.overtime1)
    print(dwr.overtime2)

print(workingHours._get_weekly_worked_hour())
print(workingHours.weekly_overtime)
print(workingHours.get_total_overtime1())
print(workingHours.get_total_overtime2())
print(workingHours.get_total_regular_hours())



#print('Weekly Hours: '+str(workingHours.getWeeklyHours()))
#print('Total Hours: '+str(workingHours.getHours()))
#print('Over Time: '+str(workingHours.getOvertime()))
#print('Over Time (Approval): '+str(workingHours.getOvertime(True)))
#print('Last Week hours: '+str(workingHours.getLastWeekHours()))
'''
d = time.strptime("22 Jul 2017", "%d %b %Y")
print(strftime("%U", d))
'''
'''
import csv
import pandas

CORRECT_MAPPING_LIST = "./Book2Sheet1.csv"
DATA_PATH = "./Book2Sheet2.csv"
OUTPUT_PATH = "./test2.csv"
FROM_COL_NUM = 0
TO_COL_NUM = 0


def csv_file_process():
    with open(CORRECT_MAPPING_LIST, 'rb') as fp:
        reader = csv.reader(fp, delimiter=',', quotechar='"')
        # next(reader, None)  # skip the headers
        correct_mapping_list = [row for row in reader]
    with open(DATA_PATH, 'r') as fp:
        reader = csv.reader(fp, delimiter=',', quotechar='"')
        # next(reader, None)  # skip the headers
        data = [row for row in reader]
        #Check empty line if line is empty set a empty string to row list
        for i in range(len(data)):
            if not data[i] :
                data[i]=['']
    rowsn_correct = len(correct_mapping_list)
    rowsn_data = len(data)

    for i in range(rowsn_correct):
        correct = correct_mapping_list[i][FROM_COL_NUM]
        for j in range(rowsn_data):
            if (data[j][TO_COL_NUM].endswith(correct) ):
                data[j][TO_COL_NUM]=correct
    rewrite_data = pandas.DataFrame(data)
    rewrite_data.to_csv(OUTPUT_PATH,index=False,header=False)

csv_file_process()

'''