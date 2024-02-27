# PyBehaviorTree
This is a minimal behavior tree implementation that follows the guide: [Implementing Behavior Trees - Renato Pereira](https://web.archive.org/web/20150216014951/http://guineashots.com/2014/09/24/implementing-a-behavior-tree-part-1/). This is intended as a minimalistic behavior tree implementation in Python with no external references. The purpose of  this module is to provide a small set of standard classes from which a large set of behaviors can be implemented. The idea is that you implement your own actions as a subclass of the `BaseNode` and put it into a tree with behaviors.

## Installation
You can test it out by running `poetry run python3 example.py`.

Then you can install it by running `poetry install`, or by building a wheel using `poetry build` and installing the wheel however you need.

## Usage
See the individual docstrings, or the examples in [examples](./examples/).