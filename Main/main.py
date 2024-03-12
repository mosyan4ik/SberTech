"""
Модуль основного действия
"""

__author__ = "mosyan4ik"

import json

from DataClass.baseclass import Document

with open('../data/initial_data_new.json', 'r', encoding='utf-8') as data_file:
    data = json.load(data_file)
    # print(data)
    doc = Document(**data)
    print(doc.tasks.get('rows')[0].get('children')[0].get('parentId'))
    # print(doc.to_json())
