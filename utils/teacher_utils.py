def teacher_shedule(teacher_timetable):
    schedule = {}
    for r in teacher_timetable:
        schedule[r['period_no']] = { "subject": r['subject_name'],"class_name": r['class_name'],"department": r['department'],"semester": r['semester'],"year":r['year'],"subject_code":r['subject_code'],"teacher_id":r['teacher_id'] }

    return schedule

def periods_calculation(result):
    today_periods = []
    today_class_count = 0

    if not result:
        return [{
            "period_no": "--",
            "class": "Holiday",

        }], 0

    today_periods = []
    for period_no in range(1, 8):
        if period_no in result:
            today_class_count+=1
            row = result[period_no]
            today_periods.append({
                "period_no": f"P:{period_no}" ,
                "subject_name": row['subject'].upper(),
                "class": row['class_name'],
                "year": row['year'],
                "department": row['department'],
                "semester": row['semester'],
                "subject_code":row['subject_code'],
                "teacher_id":row['teacher_id']
            })
        else:  
            today_periods.append({
                "period_no": f"P:{period_no}",
                "subject_name": "-",
                "class": "Free"
            })


    return today_periods, today_class_count

def teacher_pending_count(today_classes, marked_classes):
    count = today_classes - marked_classes
    return count

def load_teacher_timetable(rows):
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
            "class_name": row['class_name'],
            "year": row['year']
        }

    return timetable

from collections import defaultdict

def build_attendance_report(attendance_list):

    report = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(lambda: {
                    "total_classes": 0,
                    "present": 0
                })
            )
        )
    )

    for r in attendance_list:
        reg = r['register_no']
        subject_code = r['subject_code']
        subject_name = r['subject_name']
        name = r['name']
        status = r['status']

        report[subject_name][subject_code][reg][name]["total_classes"] += 1

        if status == "Present":
            report[subject_name][subject_code][reg][name]["present"] += 1

    return report