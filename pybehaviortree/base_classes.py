"""
This module defines base classes for a minimal behavior tree.
"""
__author__ = "Mathias Hauan Arbo"
__copyright__ = "Copyright (C) 2024 SINTEF Manufacturing"
__license__ = "LGPL-2.1-or-later"
from abc import ABC, abstractmethod
import uuid
from typing import Union, Optional, Dict, Any
import enum

class ResultType(enum.IntEnum):
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3
    ERROR = 4

class BasicBlackboard:
    """
    Basic blackboard for storing the data.

    This can be used to store data that should be available to the 
    behavior tree or its nodes at runtime. The blackboard has a "base"
    memory, tree specific memory (accessed through its id), and node
    specific memory (accessed )
    This is made so that one blackboard can contain information from
    multiple behavior trees, and nodes in a structured way.
    """
    def __init__(self):
        self._base_memory:Dict[Union[str,uuid.UUID]] = dict()
        self._tree_memory:Dict[Union[str,uuid.UUID]] = dict()
    
    def _get_tree_memory(
            self,
            tree_scope:uuid.UUID):
        """
        Internal function to get a specific tree's memory.

        If no memory is associated with the tree, a new dict will
        be created for it.

        :param tree_scope: the id of the tree in question.
        :return: the tree's specific dictionary part of the blackboard.
        """
        if not tree_scope in self._tree_memory:
            self._tree_memory[tree_scope] = {
                "node_memory":{},
                "open_nodes":[]
            }
        return self._tree_memory[tree_scope]
    
    def _get_node_memory(
            self,
            tree_memory:uuid.UUID,
            node_scope:uuid.UUID):
        """
        Internal function to get a specific node's memory.

        If no memory is associated with the node, a new dict will
        be created for it.

        :param tree_memory: the dictionary part of the blackboard for the tree.
        :param node_scope: the id of the node in question.
        :return: the node's specific dictionary part of the blackboard.
        """
        memory = tree_memory["node_memory"]
        if not node_scope in memory:
            memory[node_scope] = {}
        return memory[node_scope]
    
    def _get_memory(
            self,
            tree_scope:Optional[uuid.UUID]=None,
            node_scope:Optional[uuid.UUID]=None):
        """
        Internal function to get the appropriate memory based on scopes.

        If both tree_scope and node_scope are provided, the function will
        return the node's memory. If only the tree_scope is provided, it
        returns the tree's memory. Otherwise, it returns the base memory.

        :param tree_scope: the id of the tree in question.
        :param node_scope: the id of the node in question.
        :return: the appropriate dictionary part of the blackboard.
        """
        memory = self._base_memory
        if tree_scope is not None:
            memory = self._get_tree_memory(tree_scope)
            if node_scope is not None:
                memory = self._get_node_memory(memory, node_scope)
        return memory
    
    def set(
            self,
            key:str,
            value:Any,
            tree_scope:Optional[uuid.UUID]=None,
            node_scope:Optional[uuid.UUID]=None):
        """
        Set a value in the blackboard.

        :param key: the key to set the value for.
        :param value: the value to set.
        :param tree_scope: the id of the tree in question.
        :param node_scope: the id of the node in question.
        """
        memory = self._get_memory(tree_scope,node_scope)
        memory[key] = value

    def get(
            self,
            key:str,
            tree_scope:Optional[uuid.UUID]=None,
            node_scope:Optional[uuid.UUID]=None,
            default:Optional[Any]=None):
        """
        Get a value from the blackboard.

        :param key: the key to get the value for.
        :param tree_scope: the id of the tree in question.
        :param node_scope: the id of the node in question.
        :param default: the default value to return if the key is not found.
        :return: the value associated with the key, or the default value if not found.
        """
        memory = self._get_memory(tree_scope, node_scope)
        return memory.get(key, default)
    
    def keys(
            self,
            tree_scope:Optional[uuid.UUID]=None,
            node_scope:Optional[uuid.UUID]=None):
        """
        Get the keys stored in the blackboard.

        :param tree_scope: the id of the tree in question.
        :param node_scope: the id of the node in question.
        :return: a list of keys stored in the blackboard.
        """
        return list(self._get_memory(tree_scope, node_scope).keys())

class TickInfo:
    """
    Information container for a single tick of the behavior tree.

    This class holds information about the current state of the behavior
    tree during a single execution tick. It tracks the tree being executed,
    the currently open nodes, the count of visited nodes, and the blackboard
    associated with the execution.
    """
    def __init__(self):
        self.tree = None
        self.open_nodes = []
        self.node_count = 0
        self.blackboard:Optional[BasicBlackboard] = None

    def enter_node(self, node):
        """
        Record the entry of a node during the tick.

        :param node: The node entering during the tick.
        """
        self.node_count += 1
        self.open_nodes.append(node)
    
    def close_node(self, node):
        """
        Record the closure of a node during the tick.

        :param node: The node closing during the tick.
        """
        if node.id == self.open_nodes[-1].id:
            self.open_nodes.pop()

class BehaviorTree:
    """
    Represents a behavior tree structure.

    This class defines the structure of a behavior tree and provides
    functionality to execute the tree using a given blackboard.
    """
    def __init__(self):
        self.id = uuid.uuid4()
        self.root = None
    
    def tick(self, blackboard:BasicBlackboard)->ResultType:
        """
        Execute a single tick of the behavior tree.

        :param blackboard: The blackboard containing data relevant to the execution.
        :return: The result of the tick execution.
        """
        # Set up tick info
        tick_info = TickInfo()
        tick_info.blackboard = blackboard
        tick_info.tree = self
        
        # Run the tree
        status = self.root._execute(tick_info)

        # Close nodes from last tick
        last_open_nodes = blackboard.get("open_nodes", self.id)
        current_open_nodes = tick_info.open_nodes
        idx = None
        for idx, pair in enumerate(zip(last_open_nodes, current_open_nodes)):
            if pair[0] != pair[1]:
                break
        if idx is not None:
            for node in reversed(last_open_nodes[idx+1:]):
                node._close(tick_info)
        # Log the information
        blackboard.set("open_nodes", current_open_nodes, self.id)
        blackboard.set("node_count", tick_info.node_count, self.id)
        return status

class BaseNode(ABC):
    """
    Base class for all nodes in the behavior tree.

    This class defines the basic structure and functionality shared
    by all nodes in the behavior tree. Inheriting classes can implement
    methods for node entry, opening, ticking, closing, and exiting.

    Of these it is mandatory to always implement a method for tick.
    """
    def __init__(self, children:Optional[list]=None):
        self.id = uuid.uuid4()
        if children is not None:
            self.children = children
        else:
            self.children = []
    
    def _execute(self, tick_info:TickInfo)->ResultType:
        """
        Internal node execution method.

        :param tick_info: Information about the current tick of the tree.
        :return: The result of the node execution.
        """
        # Enter the node
        self._enter(tick_info)
        
        # Open if not already opened
        if not tick_info.blackboard.get(
                "is_open",
                tick_info.tree.id,
                self.id,
                False):
            self._open(tick_info)
        
        # Check the node
        status:ResultType = self._tick(tick_info)
        
        # Close if finished running
        if status != ResultType.RUNNING:
            self._close(tick_info)
        self._exit(tick_info)

        return status

    def _enter(self, tick_info:TickInfo)->None:
        """
        Internal node to record the entry into the node.

        :param tick_info: Information about the current tick of the tree.
        """
        tick_info.enter_node(self)
        self.enter(tick_info)
    
    def _open(self, tick_info:TickInfo)->None:
        """
        Internal node to record that we open the node for execution.

        :param tick_info: Information about the current tick of the tree.
        """
        tick_info.blackboard.set(
            "is_open",
            True,
            tick_info.tree.id,
            self.id)
        self.open(tick_info)
    
    def _tick(self, tick_info:TickInfo)->ResultType:
        """
        Internal wrapper added for future debug possibilities.

        :param tick_info: Information about the current tick of the tree.
        :return: The result of the node execution.
        """
        # Added for future debug possibilities
        return self.tick(tick_info)
    
    def _close(self, tick_info:TickInfo)->None:
        """
        Internal wrapper to record that we close the node after execution.

        :param tick_info: Information about the current tick of the tree.
        """
        tick_info.close_node(self)
        tick_info.blackboard.set(
            "is_open",
            False,
            tick_info.tree.id,
            self.id)
        self.close(tick_info)
    
    def _exit(self, tick_info:TickInfo)->None:
        """
        Internal wrapper to record the exit of the node during the tick.

        Added for future debug possibilities

        :param tick_info: Information about the current tick of the tree.
        """
        # Added for future debug possibilities
        self.exit(tick_info)
    
    def enter(self, tick_info:TickInfo)->None:
        """
        Placeholder method for node entry behavior.

        :param tick_info: Information about the current tick of the tree.
        """
        pass
    
    def open(self, tick_info:TickInfo)->None:
        """
        Placeholder method for node opening behavior.

        :param tick_info: Information about the current tick of the tree.
        """
        pass
    
    @abstractmethod
    def tick(self, tick_info:TickInfo)->ResultType:
        """
        Execute the main logic of the node during the tick.

        This method must be implemented by subclasses to define
        the behavior of the specific node type.

        :param tick_info: Information about the current tick of the tree.
        :return: The result of the node execution.
        """
        return NotImplemented
    
    def close(self, tick_info:TickInfo)->None:
        """
        Placeholder method for node closing behavior.

        :param tick_info: Information about the current tick of the tree.
        """
        pass

    def exit(self, tick_info:TickInfo)->None:
        """
        Placeholder method for node exit behavior.

        :param tick_info: Information about the current tick of the tree.
        """
        pass
    
