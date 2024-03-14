"""
Модуль основного действия
"""

__author__ = "mosyan4ik"

import json
from datetime import datetime, timedelta

from DataClass.baseclass import (Document, Intervals, Calendar, Calendars, AccountingObject, Assignment,
                                 Assignments, TimeRanges, KeyResults, Resource, Resources, Dependency,
                                 Dependencies, Task, Tasks, Project, AdditionalFields, GanttViewState,
                                 Worker)

with open('../data/initial_data_new.json', 'r', encoding='utf-8') as data_file:
    data = json.load(data_file)
    # print(data)
    doc = Document(**data)
    # print(doc.tasks.get('rows')[0].get('children')[0])  # .get('parentId'))
    # print(doc.to_json())
    # for item in doc.resources.get('rows'):
    #     print(item)

    doc_output = Document(**data)


def is_holiday(date: datetime) -> bool:
    """
    Метод отвечает на вопрос - выходной ли день?
    :param date: рассматриваемая дата
    :return:
    """
    # date_parsed = date.strftime('%Y-%m-%dT%H:%M:%S')
    return date in DATETIME_HOLIDAY_SET_2


def date_by_adding_business_days(from_date: datetime, add_days: int):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date = current_date + timedelta(days=1)
        weekday = current_date.weekday()
        if (datetime(2024, 4, 27).date() != current_date.date() and weekday >= 5) or is_holiday(weekday):  # пересмотреть рабочие дни
            continue
        business_days_to_add -= 1
    return current_date


dates = doc.calendars.get('rows')[0].get('intervals')
weekends = []
# workdays = []
NON_WORKING_INTERVALS = list(filter(lambda x: True if not x.get('isWorking') else False, dates))
NON_WORKING_INTERVALS_2 = list(filter(lambda x: True if x.get('workException') == 'WEEKEND' else False, dates))
DATETIME_HOLIDAY_SET = set(map(lambda x: datetime.strptime(x.get('startDate') or '0001-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S'), NON_WORKING_INTERVALS))
DATETIME_HOLIDAY_SET_2 = set(map(lambda x: datetime.strptime(x.get('startDate'), '%Y-%m-%dT%H:%M:%S'), NON_WORKING_INTERVALS_2))

# print(NON_WORKING_INTERVALS)
# print(NON_WORKING_INTERVALS_2)
# print(DATETIME_HOLIDAY_SET)
# print(DATETIME_HOLIDAY_SET_2)
# for item in dates:
#     cur = Intervals(**item)
#     if cur.startDate is not None and cur.workException == 'WEEKEND':
#         check = datetime.strptime(cur.startDate, '%Y-%m-%dT%H:%M:%S')
#         weekends.append(check)
# print(check.strftime('%Y-%m-%d'))
# if cur.startDate is not None and cur.workException == 'WEEKDAY':

# print(weekends)
# print(is_holiday(datetime(2024, 2, 23)))

def parse_role(elem: Task):
    #case project
    if elem.expanded == False:
        type_index = elem.name.find(' (')
        task_type = elem.name[:type_index]

        if task_type == 'Аналитика':
            role = 'Аналитик'
        elif task_type == 'Разработка':
            role = 'Разработчик'
        elif task_type == 'Тестирование':
            role = 'Тестировщик'
        else:
            role = None
        return role

    return None


tasks = [Task(**doc.tasks.get('rows')[0])]
all_tasks = []
while tasks:
    cur = tasks.pop()
    all_tasks.append(cur)
    if cur.children is not None:
        for item in cur.children:
            tasks.append(item)


analitical_tasks = []
development_tasks = []
testing_tasks = []

for item in all_tasks:
    role = parse_role(item)
    if role == 'Аналитик':
        analitical_tasks.append(item)
    elif role == 'Разработчик':
        development_tasks.append(item)
    elif role == 'Тестировщик':
        testing_tasks.append(item)
    else:
        continue

analitical_tasks.sort(key=lambda x: x.constraintDate)
for item in analitical_tasks:
    print(item.name, item.constraintDate)


for item in doc.dependencies.get('rows'):
    del item['from']
def dev_sort(dev_task: Task):
    for item in doc.dependencies.get('rows'):
        dependency = Dependency(**item)
        if dependency.toEvent == dev_task.id:
            from_id = dependency.fromEvent
    for item in analitical_tasks:
        if item.id == from_id:
            return item.endDate

def test_sort(test_task: Task):
    for item in doc.dependencies.get('rows'):
        dependency = Dependency(**item)
        if dependency.toEvent == test_task.id:
            from_id = dependency.fromEvent
    for item in development_tasks:
        if item.id == from_id:
            return item.endDate

print('______________________________')

# development_tasks.sort(key=dev_sort)
# for item in development_tasks:
#     print(item.name, item.endDate)

workers = doc.resources.get('rows')
all_workers = []
for item in workers:
    if item['name'].find('(') != -1:
        slave = Worker(**item)
        all_workers.append(slave)
# for item in all_workers:
#     print(item)

role_workers = list(filter(lambda x: True if x.projectRole == 'Аналитик' else False, all_workers))
for item in role_workers:
    print(item)

best = min(role_workers, key=lambda x: x.cost)
print(best)

def allocate_task_analisys(worker: Worker, task: Task):
    if len(worker.timeline) > 0:
        last_work_enddate = worker.timeline[next(reversed(worker.timeline))][1]
        start_date = date_by_adding_business_days(last_work_enddate,1)
    else:
        # print(datetime.strftime(task.constraintDate, '%Y-%m-%dT%H:%M:%S'))
        # start_date = task.constraintDate
        # task.constraintDate
        start_date = task.constraintDate
        start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
        if start_date.hour == 8:
            start_date += timedelta(minutes=45)
    end_date = date_by_adding_business_days(start_date, task.effort)
    worker.timeline[task.id] = (start_date, end_date)
    worker.total_cost += task.effort * worker.cost * 8
    task.startDate = start_date
    task.endDate = end_date + timedelta(hours=9)
    print(f'task {task.name} was allocated to {worker.name}')

def allocate_task_development(worker: Worker, task: Task):
    if len(worker.timeline) > 0:
        last_work_enddate = worker.timeline[next(reversed(worker.timeline))][1]
        prev_work_enddate = dev_sort(task)
        beginning = max(last_work_enddate, prev_work_enddate)
        start_date = date_by_adding_business_days(beginning,1)
    else:
        prev_work_enddate = dev_sort(task)
        start_date = date_by_adding_business_days(prev_work_enddate, 1)
    end_date = date_by_adding_business_days(start_date, task.effort)
    worker.timeline[task.id] = (start_date, end_date)
    worker.total_cost += task.effort * worker.cost * 8
    task.startDate = start_date
    task.endDate = end_date + timedelta(hours=9)
    print(f'task {task.name} was allocated to {worker.name}')


def allocate_task_testing(worker: Worker, task: Task):
    if len(worker.timeline) > 0:
        last_work_enddate = worker.timeline[next(reversed(worker.timeline))][1]
        prev_work_enddate = test_sort(task)
        beginning = max(last_work_enddate, prev_work_enddate)
        start_date = date_by_adding_business_days(beginning, 1)
    else:
        prev_work_enddate = test_sort(task)
        start_date = date_by_adding_business_days(prev_work_enddate, 1)
    end_date = date_by_adding_business_days(start_date, task.effort)
    worker.timeline[task.id] = (start_date, end_date)
    worker.total_cost += task.effort * worker.cost * 8
    task.startDate = start_date
    task.endDate = end_date + timedelta(hours=9)
    print(f'task {task.name} was allocated to {worker.name}')


for item in analitical_tasks:
    allocate_task_analisys(best, item)

print(best.total_cost)

development_tasks.sort(key=dev_sort)
for item in development_tasks:
    print(item.name, item.endDate)

role_workers_dev = list(filter(lambda x: True if x.projectRole == 'Разработчик' else False, all_workers))
for item in role_workers_dev:
    print(item)

best_dev = min(role_workers_dev, key=lambda x: x.cost)
print(best_dev)

for item in development_tasks:
    allocate_task_development(best_dev, item)

print(best_dev.total_cost)

testing_tasks.sort(key=test_sort)
for item in testing_tasks:
    print(item.name, item.endDate)

role_workers_test = list(filter(lambda x: True if x.projectRole == 'Тестировщик' else False, all_workers))
for item in role_workers_test:
    print(item)

best_test = min(role_workers_test, key=lambda x: x.cost)
print(best_test)

for item in testing_tasks:
    allocate_task_testing(best_test, item)

print(best_test.total_cost)

# print(doc.tasks.get('rows')[0]['id'])
# print(doc.tasks.get('rows')[0])
# print(doc.tasks.get('rows'))
# print(doc.tasks)

# for item in all_tasks:
#     if doc.tasks.get('rows')[0].get('children')[0].get('children')[0] == item.id:
        # doc_output.tasks.get('rows')[0].get('children')[0].get('children')[0].get('startDate')
print(doc_output.tasks.rows)
        # print(item)



# print(doc_output)

doc_output.output_json()
# jason = doc.to_json()
# with open('output.json', 'w') as f:
#     json.dump(asdict(), f)





