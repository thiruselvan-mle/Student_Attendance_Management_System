from datetime import date
from calendar import monthrange

def calculate_percentage(attendance):
    total_present = 0
    total_absent = 0

    for s in attendance:
        status = s['status']

        if status == "Present":
            total_present +=1

        elif status == "Absent":
            total_absent +=1
    
    total_periods = total_present + total_absent
    if total_present != 0:
        overall_percentage = round((total_present/total_periods)*100)
    else:
        overall_percentage = 0
    return overall_percentage

def incharge_shedule(incharge_timetable):
    schedule = {}
    for r in incharge_timetable:
        schedule[r['period_no']] = { "subject": r['subject_name'],"class_name": r['class_name'],"department": r['department'],"semester": r['semester'],"year":r['year'],"subject_code":r['subject_code'],"teacher_id":r['teacher_id'] }

    return schedule

def today_incharge_periods(result):
    today_periods = []

    if not result:
        return [{
            "period_no": "--",
            "subject_name": "Holiday",

        }]

    for period_no in range(1, 8):
        if period_no in result:
            row = result[period_no]
            today_periods.append({
                "period_no": f"P:{period_no}",
                "subject_name": row['subject'].upper(),
                "teacher_id":row['teacher_id'],
                "class": row['class_name'],
                "year": row['year'],
                "department": row['department'],
                "semester": row['semester'],
                "subject_code":row['subject_code']
            })
        else:  
            today_periods.append({  
                "period_no": f"P:{period_no}",
                "subject_name": "Free",
            })

    return today_periods

def count_students(students, gender):
    total_students = 0
    male_count = 0
    female_count =0
    for s in students:
        if s:
            total_students +=1
            
    for g in gender:
        if g.lower() == 'male':
            male_count += 1

        else:
            female_count += 1

    return total_students, male_count, female_count

def load_incharge_timetable(rows):
    timetable = {}

    for row in rows:
        day = row['day']
        period_no = row['period_no']


        if day not in timetable:

            timetable[day] = [
                {
                    "period_no": i,
                    "subject_name": "Free"
                } for i in range(1, 8)
            ]

        timetable[day][period_no - 1] = {
            "period_no": period_no,
            "subject_name": row['subject_name'],
        }

    return timetable

def month_calculation(selected_month,today,year):

    if not selected_month:
        selected_month = today.month

    month_start = date(year, selected_month, 1)
    last_day = monthrange(year, selected_month)[1]
    month_end = date(year, selected_month, last_day)

    return month_start, month_end

def students_monthly_report(rows):
    report = {}
    total_days = 0
  
    for r in rows:
        reg_no = r['register_no']
        name = r["name"]
        status = r["status"]
        
        if reg_no not in report:
            report[reg_no]= { 
            "name":name,
            "total_present":0 ,
            "total_absent":0,
            "total_periods":0,
            "percentage":0
            }

        if status == 'Present':
            report[reg_no]["total_present"] += 1

        else:
            report[reg_no]["total_absent"] += 1

        report[reg_no]["total_periods"] += 1

    for reg_no in report:
        total = report[reg_no]["total_periods"]
        persent = report[reg_no]["total_present"]
        report[reg_no]["percentage"] = round((persent/total)*100)
        total_days = total // 7

    return report , total_days
