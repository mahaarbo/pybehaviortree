"""
Short hello world example

This example shows a print node accessing a field on the blackboard and printing its value.
"""
import pybehaviortree as pbt

# The main tree that will be traversed
tree = pbt.BehaviorTree()

# The storage unit for global variables, per-tree variables, and per-node-in tree variables
blackboard = pbt.BasicBlackboard()

# The action node we will use
print_node = pbt.actions.PrintNode()

# Set an arbitrary field in the blackboard to a value
blackboard.set("my_data_key", "Hello world")

# Store the "my_data_key" as the relevant key in the print_node's part of the blackboard
print_node.set_key("my_data_key", blackboard, tree.id)

# Set the print node as the root
tree.root = print_node

# Then traverse the tree
tree.tick(blackboard)
