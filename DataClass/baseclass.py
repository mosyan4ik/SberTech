"""
Базовый класс представления данных
"""

__author__ = "mosyan4ik"

import json
from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Optional, List, ForwardRef


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
    _from: str
    toEvent: str
    to: str
    lag: int
    lagUnit: date
    type: int
    active: bool
    guid: str
    id: str


@dataclass
class Dependencies:
    rows: List[Dependency]

    def __post_init__(self):
        self.rows = self.rows and [Dependency(**row) for row in self.rows]


@dataclass
class Task:
    parentId: Optional[str]
    children: Optional[List[ForwardRef("Task")]]
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
    rollup: bool
    inactive: bool
    critical: Optional[bool]
    rootTask: bool
    priority: int
    assignmentsUnitsSum: int
    guid: str
    id: str

    def __post_init__(self):
        self.children = self.children and [Task(**child) for child in self.children]


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
