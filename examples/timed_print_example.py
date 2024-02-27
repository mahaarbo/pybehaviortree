"""
Timed print example.

This example is a bit daedal with many moving gears, but the intent
is to show how some of the different nodes operate.
The tree is supposed to do something akin to
```python
count = 0
for _ in range(5):
    time.sleep(1)
    print("Hello world!)
    count += 1
    print(count)
```

And it achieves this using the wait node and the print node as actions.
"""
import pybehaviortree as pbt
import time
# Our main tree
tree = pbt.BehaviorTree()
# And our main blackboard
blackboard = pbt.BasicBlackboard()

# Let's start with a little branch that will count and print hello world
# then print the count
hello_node = pbt.actions.PrintNode()
count_decorator = pbt.decorators.CountNode([hello_node])
print_count_node = pbt.actions.PrintNode()
print_sequence = pbt.composites.SequenceNode([count_decorator, print_count_node])


# Remember to print "hello world!"
hello_node.set_key("hello_key", blackboard, tree.id)
blackboard.set("hello_key", "Hello world!")

# Remember to print count from the count key
print_count_node.set_key("count", blackboard, tree.id)
# In the count_dec node
print_count_node.set_node_id(count_decorator.id, blackboard, tree.id)
# In the same tree as we arein
print_count_node.set_tree_id(tree.id, blackboard, tree.id)

# Then let's move on to a pattern that will only tick the count_dec if
# we are not waiting
wait_node = pbt.actions.WaitNode()
inverter_decorator = pbt.decorators.InverterNode([wait_node])
wait_selector = pbt.composites.SelectorNode([
    inverter_decorator,
    print_sequence,
])

# Remember to set the wait duration
wait_node.set_duration(1, blackboard, tree.id)

# Then let's just do a simple sequence over these, but we have to remember where we left off so
# don't perform the same branch twice if we encounter a running branch.
memory_sequence5 = pbt.composites.MemSequenceNode([wait_selector]*5)

# The use of MemSequenceNode here is important because sequence node will always
# try to get a success from ALL of its children each tick. That means we will
# have something that runs forever as our wait node is guaranteed to return running the first
# time it is visited.

# So we set the root to the memory sequence node
tree.root = memory_sequence5

# Now let's run this until we get success from the tree, and log some simple
# timing results.
start_time = time.time()
num_ticks = 0
while tree.tick(blackboard) == pbt.ResultType.RUNNING and num_ticks < 1e6:
    num_ticks += 1
end_time = time.time()
total_time = end_time - start_time
print("Total time:", total_time)
print("Number of ticks:", num_ticks)
print("Time per tick:", 1e6*total_time/num_ticks, "microseconds")
print("Tick frequency:", num_ticks/total_time)

# This TickInfo object is basically what is propagated down the tree
# at each tick. So it's added if you want to try to tick any of the sub-branches
# yourself.
tick_info = pbt.TickInfo()
tick_info.tree = tree
tick_info.blackboard = blackboard