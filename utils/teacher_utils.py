from collections import defaultdict

def teacher_shedule(teacher_timetable):
    schedule = defaultdict(list)

    for r in teacher_timetable:
        schedule[r['period_no']].append({
            "subject": r['subject_name'],
            "department": r['department'],
            "semester": r['semester'],
            "year": r['year'],
            "subject_code": r['subject_code'],
            "teacher_id": r['teacher_id']
        })

    return schedule

def periods_calculation(result):
    today_periods = []
    today_class_count = 0

    if not result:
        return [{
            "period_no": "--",
            "class": "Free"
        }], 0

    # result = { period_no: [class1, class2] }

    for period_no in sorted(result.keys()):
        classes = result[period_no]

        today_class_count += len(classes)

        today_periods.append({
            "period_no": f"P:{period_no}",
            "classes": [
                {
                    "subject_name": c['subject'].upper(),
                    "department": c['department'],
                    "semester": c['semester'],
                    "year": c['year'],
                    "subject_code": c['subject_code'],
                    "teacher_id": c['teacher_id']
                }
                for c in classes
            ]
        })

    return today_periods, today_class_count

def teacher_pending_count(today_classes, marked_classes):
    if today_classes < marked_classes:
        return 0 , today_classes
    else:
        count = today_classes - marked_classes
        return count, marked_classes

def load_teacher_timetable(rows):
    timetable = {}

    for row in rows:
        day = row['day']
        period_no = row['period_no']

        if day not in timetable:
            timetable[day] = [
                {
                    "period_no": i,
                    "classes": []   
                } for i in range(1, 8)
            ]

        timetable[day][period_no - 1]["classes"].append({
            "subject_name": row['subject_name'],
            "department": row['department'],
            "year": row['year']
        })

    return timetable

def build_attendance_report(attendance_list):

    report = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(lambda: {
                        "total_classes": 0,
                        "present": 0
                    })
                )
            )
        )
    )

    for r in attendance_list:
        reg = r['register_no']
        subject_code = r['subject_code']
        subject_name = r['subject_name']
        department = r['department']
        name = r['name']
        status = r['status']

        report[subject_name][subject_code][department][reg][name]["total_classes"] += 1

        if status == "Present":
            report[subject_name][subject_code][department][reg][name]["present"] += 1

    return report

