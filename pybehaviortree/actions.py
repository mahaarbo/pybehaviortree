"""
This module defines two common action nodes for the minimal behavior tree.
"""
__author__ = "Mathias Hauan Arbo"
__copyright__ = "Copyright (C) 2024 SINTEF Manufacturing"
__license__ = "LGPL-2.1-or-later"
from .base_classes import BaseNode, ResultType, TickInfo, BasicBlackboard
from uuid import UUID
import time
from typing import Union

class WaitNode(BaseNode):
    """
    Action node that waits a specific amount of time.
    
    This is a leaf node in a behavior tree, and will return running 
    at each tick while we still need to wait.
    Returns success when we have waited long enough.
    Cannot return failure.
    """
    def set_duration(self, duration:float, blackboard:BasicBlackboard, tree_id:UUID):
        """
        Set the duration that we should wait.

        :param duration: Time in seconds to wait
        :param blackboard: The blackboard we will be using
        :param tree_id: The tree id we will be using
        """
        blackboard.set(
            "duration",
            duration,
            tree_id,
            self.id
        )
    
    def open(self, tick_info:TickInfo)->None:
        """
        Open the node, remains open until not running.

        :param tick_info: The tick info propagating through the tree.
        """
        tick_info.blackboard.set(
            "start_time",
            time.time(),
            tick_info.tree.id,
            self.id
        )
    
    def tick(self, tick_info:TickInfo)->ResultType:
        """
        Tick the wait node.
        
        :param tick_info: The tick info propagating through the tree.
        :return: Either Running or Success.
        """
        wait_duration = tick_info.blackboard.get(
            "duration",
            tick_info.tree.id,
            self.id
        )
        start_time = tick_info.blackboard.get(
            "start_time",
            tick_info.tree.id,
            self.id
        )
        if time.time() - start_time < wait_duration:
            return ResultType.RUNNING
        return ResultType.SUCCESS

class PrintNode(BaseNode):
    """
    Action node that prints an object in the blackboard.

    This is a leaf node in a behavior tree, and returns success if it has a 
    key to get from the blackboard, or error if there is no key set.
    We will look for the data in the field we set as "key" under "node_id" in the "tree_id" tree.
    """
    def set_node_id(self, other_node_id:UUID, blackboard:BasicBlackboard, own_tree_id:UUID):
        """
        Set the node id of where to find the value.

        :param other_node_id: The id of the node where we will find the object
        :param blackboard: The blackboard we are using
        :param own_tree_id: The id of the tree we are in.
        """
        blackboard.set(
            "other_node_id",
            other_node_id,
            own_tree_id,
            self.id
        )

    def set_tree_id(self, other_tree_id:UUID, blackboard:BasicBlackboard, own_tree_id:UUID):
        """
        Set the tree id of where to find the value.


        """
        blackboard.set(
            "other_tree_id",
            other_tree_id,
            own_tree_id,
            self.id
        )

    def set_key(self, key:Union[str,UUID], blackboard:BasicBlackboard, own_tree_id:UUID):
        blackboard.set(
            "print_key",
            key,
            own_tree_id,
            self.id
        )

    def tick(self, tick_info:TickInfo)->ResultType:
        """
        Tick the print node.

        :param tick_info:
        :return: success, or error if the print_key is not found.
        """
        print_key = tick_info.blackboard.get(
            "print_key",
            tick_info.tree.id,
            self.id
        )
        # If we don't have a print_key, that is an error
        if print_key is None:
            return ResultType.ERROR
        # Tree_id and node_id can be None, in which case we just
        # access the "global" values
        tree_id = tick_info.blackboard.get(
            "other_tree_id",
            tick_info.tree.id,
            self.id
        )
        node_id = tick_info.blackboard.get(
            "other_node_id",
            tick_info.tree.id,
            self.id
        )
        print(tick_info.blackboard.get(
            print_key,
            tree_id,
            node_id
        ))
        return ResultType.SUCCESS