"""
This module defines four common decorator nodes for the minimal behavior tree.
"""
__author__ = "Mathias Hauan Arbo"
__copyright__ = "Copyright (C) 2024 SINTEF Manufacturing"
__license__ = "LGPL-3.0-or-later"
from .base_classes import ResultType, TickInfo, BaseNode

class SequenceNode(BaseNode):
    """
    Composite node that tries to tick all its children each time it is ticked.

    If a child returns failure then the iteration is stopped and this node returns
    failure. Similarly if a child returns running, this will return running.
    If all the chilren return success, then this node will return success as well.

    This node does not remember its position, so during the next tick, it will start
    from the beginning of the list of children again and try to tick each of them.

    This can be used to check multiple things you expect to succeed each iteration,
    and can be thought of sort of like the boolean "and" operation.
    """
    def tick(self, tick_info:TickInfo)->ResultType:
        """
        Tick the sequence node.

        :param tick_info: The tick info propagated through the tree.
        :result: Success if all children returned success, otherwise returns what the child returned.
        """
        for child in self.children:
            status = child._execute(tick_info)
            if status != ResultType.SUCCESS:
                return status
        return ResultType.SUCCESS

class SelectorNode(BaseNode):
    """
    Composite node that tries to tick all its children each time it is ticked.

    If a child returns success, then the iteration is stopped and this returns success.
    Similarly if a child returns running, this will returns running. If all the children
    return failure, then this node will return failure as well.

    This node does not remember its postiion, so during the next tick, it will start
    from the beginning of the list of its children again, and try to tick each of them until
    one succeeds.

    This can be used to "select" a node from multiple that can fail, and can be thought of
    sort of like the boolean "or" operation.
    """
    def tick(self, tick_info:TickInfo)->ResultType:
        """
        Tick the selector node.
        
        :param tick_info: The tick info propagated through the tree
        :result: Failure if all children fail, otherwise same as the child returned.
        """
        for child in self.children:
            status = child._execute(tick_info)
            if status != ResultType.FAILURE:
                return status
        return ResultType.FAILURE

class MemSequenceNode(BaseNode):
    """
    Composite node that tries to tick all its children but remembers where it left off.

    If a child returns failure then the iteration is stopped and this node returns failure.
    Similarly if a child returns running, this will return running.
    If all the children return success, then this node will return success.

    The big difference between this and SequenceNode is that this one will continue from the
    child that was last running. So if a node returns running, we will continue iterating over 
    the children from that one during the next tick. If any child returns failure, we will 
    still return failure and start from the beginning again.

    This can be used to handle long-running tasks better without starting from the beginning.
    """
    def tick(self, tick_info:TickInfo)->ResultType:
        """
        Tick the memsequence node.

        :param tick_info: The tick info propagated through the tree
        :result: Success if all children returned success, otherwise returns what the child returned.
        """
        running_child_idx = tick_info.blackboard.get(
            "running_child_idx",
            tick_info.tree.id,
            self.id,
            0
        )
        for idx in range(running_child_idx, len(self.children)):
            status = self.children[idx]._execute(tick_info)
            if status == ResultType.RUNNING:
                tick_info.blackboard.set(
                    "running_child_idx",
                    idx,
                    tick_info.tree.id,
                    self.id
                )
                return status
            elif status != ResultType.SUCCESS:
                return status
        return ResultType.SUCCESS

class MemSelectorNode(BaseNode):
    """
    Composite node that tries to tick all its children each time it is ticked.

    If a child returns success, then the iteration is stopped and this returns success.
    Similarly if a child returns running, this will return running. If all the children
    return failure, then this node will return failure as well.

    The big difference between this and SelectorNode is that this one will continue from
    the child that was last running. So if a node returns running, we will continue iterating 
    over the children from that one during the next tick. If any child returns success, we will
    still return success and start from the beginning again.
    """
    def tick(self, tick_info:TickInfo):
        """
        Tick the memselector node.
        
        :param tick_info: The tick info propagated through the tree
        :result: Failure if all children fail, otherwise same as the child returned.
        """
        running_child_idx = tick_info.blackboard.get(
            "running_child_idx",
            tick_info.tree.id,
            self.id,
            0
        )
        for idx in range(running_child_idx, len(self.children)):
            status = self.children[idx]._execute(tick_info)
            if status == ResultType.RUNNING:
                tick_info.blackboard.set(
                    "running_child-idx",
                    idx,
                    tick_info.tree.id,
                    self.id
                )
                return status
            elif status != ResultType.FAILURE:
                return status
        return ResultType.FAILURE

