import nbformat

from .group import GroupSequence
from .cell import Cell

from collections import defaultdict


class Notebook(GroupSequence):
    
    def __init__(self, filename, indexes=None, counts=None, order=None, **kwargs):
        if not 'group_margin' in kwargs:
            kwargs['group_margin'] = 0
        super().__init__(**kwargs)
        self.filename = filename
        self._select_by_index = indexes
        self._select_by_count = counts
        self._index_operations = defaultdict(list)
        self._count_operations = defaultdict(list)
        self._order = order
        
    def select_index(self, *indexes):
        if self._select_by_index is None:
            self._select_by_index = []
        for index in indexes:
            self._select_by_index.append(index)
        return self
        
    def select_count(self, *counts):
        if self._select_by_count is None:
            self._select_by_count = []
        for count in counts:
            self._select_by_count.append(count)
        return self

    def index_operation(self, index, operation, *value):
        self._index_operations[index].append((operation, value))
        return self
        
    def count_operation(self, count, operation, *value):
        self._count_operations[count].append((operation, value))
        return self
        
    def select_index_operate(self, index, operation, *value):
        self.select_index(index)
        self.index_operation(index, operation, *value)
        return self
        
    def select_count_operate(self, count, operation, *value):
        self.select_count(count)
        self.count_operation(count, operation, *value)
        return self
        
    def build(self, style):
        nb = nbformat.read(open(self.filename), as_version=4)
        if not self._select_by_index and not self._select_by_count:
            cell_indexes = range(len(nb['cells']))
        else:
            cell_indexes = self._select_by_index or []
        if self._select_by_count:
            for index, cell in enumerate(nb['cells']):
                if cell.get('execution_count', None) in self._select_by_count:
                    cell_indexes.append(index)
        # Add items in other
        order = self._order or range(len(cell_indexes))
        self.items = []
        for oi in order:
            if oi < len(cell_indexes):
                index = cell_indexes[oi]
                ec = nb['cells'][index].get('execution_count', None)
                cell = Cell(nb['cells'][index])
                for op, value in self._index_operations.get(index, []):
                    getattr(cell, op)(*value)
                for op, value in self._count_operations.get(ec, []):
                    getattr(cell, op)(*value)
                self.add(cell)
        for oi in range(len(cell_indexes)):
            if oi not in order:
                index = cell_indexes[oi]
                ec = nb['cells'][index].get('execution_count', None)
                cell = Cell(nb['cells'][index])
                for op, value in self._index_operations.get(index, []):
                    getattr(cell, op)(*value)
                for op, value in self._count_operations.get(ec, []):
                    getattr(cell, op)(*value)
                self.add(cell)
        super().build(style)
        
    def __repr__(self):
        return f'Notebook({self.filename!r})'
