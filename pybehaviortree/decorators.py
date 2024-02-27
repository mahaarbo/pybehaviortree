"""
This module defines two common decorator nodes for the minimal behavior tree.
"""
__author__ = "Mathias Hauan Arbo"
__copyright__ = "Copyright (C) 2024 SINTEF Manufacturing"
__license__ = "LGPL-3.0-or-later"
from .base_classes import BaseNode, ResultType, TickInfo, BasicBlackboard
from typing import Optional
from uuid import UUID
import time

class InverterNode(BaseNode):
    """
    Decorator node that inverts the result of the child.

    If the child returns success, this returns failure, and vice-versa.
    The node returns running or error if the child returns running or error.
    """
    def tick(self, tick_info:TickInfo)->ResultType:
        """
        Tick the inverter decorator.

        :param tick_info: The tick info propagated through the tree.
        :result: Success if the child returns Failure, and vice-versa. Running if child returns running.
        """
        if len(self.children) != 1:
            return ResultType.ERROR
        
        status = self.children[0]._execute(tick_info)
        if status == ResultType.SUCCESS:
            return ResultType.FAILURE
        elif status == ResultType.FAILURE:
            return ResultType.SUCCESS
        else:
            return status
        
class TimeoutNode(BaseNode):
    """
    Decorator node that will return failure if the child node takes too long time.

    If the child returns failure, this will return failure. If the child returns success, this
    will return success. But if the child returns running, this will only return running until a specific
    amount of time has passed (max_time in seconds), after which this node will return failure.
    """
    def set_duration(self, duration:float, blackboard:BasicBlackboard, tree_id:UUID)->None:
        """
        Set the duration that the timeout decorator should accept the running state.

        :param duration: Timeout duration in seconds.
        :param blackboard: The blackboard we will be using.
        :param tree_id: the id of the tree we will be in.
        """
        blackboard.set(
            "duration",
            duration,
            tree_id,
            self.id)

    def open(self, tick_info:TickInfo)->None:
        """
        Sets the start time from when the node was opened.
        """
        tick_info.blackboard.set(
            "start_time",
            time.time(),
            tick_info.tree.id,
            self.id
        )
    
    def tick(self, tick_info:TickInfo)->ResultType:
        """
        Tick the timeout decorator.

        :param tick_info: The tick info propagated through the tree.
        :result: If the child returns running or success during the timeout period, it will return running. 
        If we exceed the timeout period or the child returns failure, it return failure.
        """
        if len(self.children) != 1:
            return ResultType.ERROR
        timeout_duration = tick_info.blackboard.get(
            "duration",
            tick_info.tree.id,
            self.id
        )
        start_time = tick_info.blackboard.get(
            "start_time",
            tick_info.tree.id,
            self.id
        )
        if time.time() - start_time > timeout_duration:
            return ResultType.FAILURE
        status = self.children[0]._execute(tick_info)
        return status

class CountNode(BaseNode):
    """
    Decorator node that will count the number of times its child has been ticked.

    Returns the same value as its child, but stores the count in a variable called "count",
    in its node memory.
    """
    def tick(self, tick_info:TickInfo)->ResultType:
        """
        Tick the count node.

        :param tick_info: The tick info propagated through the tree.
        :result: Always returns the child's results, but increases the count after the 
        child has been ticked.
        """
        if len(self.children) != 1:
            return ResultType.ERROR
        
        count = tick_info.blackboard.get(
            "count",
            tick_info.tree.id,
            self.id,
            0
        )
        count += 1
        status = self.children[0].tick(tick_info)
        tick_info.blackboard.set(
            "count",
            count,
            tick_info.tree.id,
            self.id
        )
        return status