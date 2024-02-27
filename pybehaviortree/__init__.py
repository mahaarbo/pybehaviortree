"""
This module implements a minimal behavior tree.

The behavior tree implementation follows the guide:
https://web.archive.org/web/20150216014951/http://guineashots.com/2014/09/24/implementing-a-behavior-tree-part-1/
and is a minimalistic behavior tree implementation in python with no external dependencies.
The purpose of this module is to provide a small set of standard classes from which a large set of
behaviors can be implemented.
"""
__author__ = "Mathias Hauan Arbo"
__copyright__ = "Copyright (C) 2024 SINTEF Manufacturing"
__license__ = "LGPL-3.0-or-later"
from .base_classes import ResultType, BasicBlackboard, TickInfo, BaseNode, BehaviorTree
from . import actions
from . import decorators
from . import composites