"""
Базовый класс представления данных
"""

__author__ = "mosyan4ik"

import json
from collections import OrderedDict
from dataclasses import dataclass, asdict, field
from datetime import datetime, date
from typing import Optional, List, ForwardRef, Union


@dataclass
class Intervals:
    recurrentStartDate: Optional[str]
    recurrentEndDate: Optional[str]
    isWorking: bool
    name: Optional[str]
    startDate: datetime
    endDate: datetime
    priority: int
    recurrentWeekday: Optional[str]
    workException: Optional[str]
    overriddenWorkDayTimeInterval: Optional[str]


@dataclass
class Calendar:
    id: int
    name: str
    expanded: bool
    lastSaveDate: datetime
    isOverriddenDateGrid: bool
    intervals: Intervals

    def __post_init__(self):
        self.intervals = Intervals(**self.intervals)


@dataclass
class Calendars:
    rows: List[Calendar]

    def __post_init__(self):
        self.rows = self.rows and [Calendar(**row) for row in self.rows]


@dataclass
class AccountingObject:
    id: str
    name: str
    startDate: date
    endDate: date
    type: str


@dataclass
class Assignment:
    event: str
    resource: str
    units: int
    startDate: datetime
    endDate: datetime
    currentEffort: int
    guid: str
    id: str


@dataclass
class Assignments:
    rows: List[Assignment]

    def __post_init__(self):
        self.rows = self.rows and [Assignment(**row) for row in self.rows]


@dataclass
class TimeRanges:
    rows: List


@dataclass
class KeyResults:
    rows: List


@dataclass
class Resource:
    name: str
    projectRole: str
    reservationType: str
    reservationPercent: int
    reservationStatus: str
    projectRoleId: str
    id: str


@dataclass
class Resources:
    rows: List[Resource]

    def __post_init__(self):
        self.rows = self.rows and [Resource(**row) for row in self.rows]


@dataclass
class Dependency:
    fromEvent: str
    # from: str
    toEvent: str
    to: str
    lag: int
    lagUnit: date
    type: int

    guid: str
    id: str

    active: Optional[bool] = None

@dataclass
class Dependencies:
    rows: List[Dependency]

    def __post_init__(self):
        self.rows = self.rows and [Dependency(**row) for row in self.rows]


@dataclass
class Task:


    name: str
    startDate: datetime
    endDate: datetime
    effort: int
    effortUnit: str
    duration: int
    durationUnit: str
    percentDone: int
    schedulingMode: str
    manuallyScheduled: bool
    effortDriven: bool
    parentIndex: int
    expanded: bool

    inactive: bool

    rootTask: bool
    priority: int
    assignmentsUnitsSum: int
    guid: str
    id: str

    # первая строчка
    parentId: Optional[str] = None
    #вместо первого пропуска
    rollup: Optional[bool] = None
    #вместо второго пропуска
    critical: Optional[bool] = None

    constraintType: Optional[str] = None
    constraintDate: Optional[datetime] = None

    children: Optional[List[ForwardRef("Task")]] = None

    def __post_init__(self):
        self.children = self.children and [Task(**child) for child in self.children]
        self.rollup = self.rollup and False


@dataclass
class Tasks:
    rows: List[Task]

    def __post_init__(self):
        self.rows = self.rows and [Task(**row) for row in self.rows]


@dataclass
class Project:
    id: str
    projectId: str
    name: str
    isReadOnly: bool
    calendar: str
    planType: str
    lastModifyDate: datetime
    lastModifyUser: Optional[str]
    publishDate: Optional[datetime]
    startDate: date
    createAccObjWorkflowStatusId: Optional[str]
    lastModifyAccObjWorkflowStatusId: Optional[str]
    lastTrackerSyncDate: Optional[datetime]


@dataclass
class AdditionalFields:
    rows: List


@dataclass
class GanttViewState:
    rows: List


@dataclass
class Document:
    requestId: str
    project: Project
    success: bool
    tasks: Tasks
    dependencies: Dependencies
    calendars: Calendars
    resources: Resources
    assignments: Assignments
    timeRanges: TimeRanges
    keyResults: KeyResults
    additionalFields: AdditionalFields
    ganttViewState: GanttViewState
    accountingObject: AccountingObject

    def to_json(self):
        return json.dumps(asdict(self), indent=4)

    def output_json(self):
        with open('output.json', 'w') as f:
            json.dump(asdict(self), f, indent=4, ensure_ascii=False)


class Timeline(OrderedDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.move_to_end(key)


class Worker(Resource):
    cost = None
    timeline = None
    total_cost = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.get_cost()
        self.timeline = Timeline()

    def get_cost(self):
        cost_start_index = self.name.find('(')
        cost_end_index = self.name.find('руб/час')
        cost_substring = self.name[cost_start_index + 1:cost_end_index]
        if cost_substring.isnumeric():
            cost = int(cost_substring)
            self.cost = cost
        else:
            print('wrong slice for resource price check')
