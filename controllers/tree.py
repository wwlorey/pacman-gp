import random


MAX_NODE_ID = 10000


class Node:
    def __init__(self, value=None):
        """Initializes the Node class (part of the binary Tree class)."""
        self.value = value
        self.children = []
        self.id = random.randint(0, MAX_NODE_ID)


    def __eq__(self, other):
        return self.value == other.value and self.children == other.children


    def __hash__(self):
        return self.id


    def __str__(self):
        """Prints this node to the screen"""
        return str(self.value)
    
    
    def left(self):
        """Returns this node's left child."""
        if len(self.children):
            return self.children[0]
        
        return None


    def right(self):
        """Returns this node's right child."""
        if len(self.children):
            return self.children[1]
        
        return None
    

    def is_leaf(self):
        """Returns True if this node is a leaf node (i.e.
        it has no children), False otherwise.
        """
        return not len(self.children)
        
    
    def add_child(self, child_value):
        """Adds the given child to self.children, while maintaining
        the binary tree property.
        """
        if len(self.children) < 2:
            self.children.append(Node(child_value))


    def add_children(self, children_values):
        """Adds the given list of children to self.children."""
        for child_value in children_values:
            self.add_child(child_value)


    def kill_all_children(self):
        """Removes all children from the this node."""
        self.children = []
        

class Tree:
    def __init__(self, config, root_value=None):
        """Initializes the (binary) Tree class."""
        self.root = Node(root_value)


    def get_height(self):
        """Returns the maximum depth (height) of this tree."""

        def get_height_recursive(node, depth=1):
            if not len(node.children):
                # This is a leaf node
                return depth

            # This is not a leaf node
            max_depth = depth
            for child in node.children:
                max_depth = max(child, depth + 1)

            return max_depth

        return get_height_recursive(self.root)


    def add_node(self, value, parent_node=None):
        """Adds a new node with provided value to the node denoted by
        parent_node.

        If parent_node is not specified, the child node is added to the root node.
        """
        if not parent_node:
            parent_node = self.root
        
        parent_node.add_child(value)


    def remove_subtree(self, subtree_parent=None):
        """Removes the subtree with root denoted by subtree_parent (not including the root).

        If subtree_parent is not provided, self.root's children are removed.
        """
        if not subtree_parent:
            subtree_parent = self.root

        subtree_parent.kill_all_children()


    def get_node_list(self):
        """Returns a list of all nodes in the tree."""
        # Create a queue of nodes
        q = []
        q.append(self.root)

        node_list = []

        while len(q):
            node = q.pop(0)

            node_list.append(node)

            for child in node.children:
                q.append(child)

        return node_list


    def visualize(self):
        """Prints this tree to the screen."""
        # Create a queue of (node, depth)
        q = []
        prev_depth = 1
        q.append((self.root, prev_depth))

        while len(q):
            node, depth = q.pop(0)

            if depth > prev_depth:
                prev_depth = depth
                print()

            print(str(node), end=', ')

            for child in node.children:
                q.append((child, depth + 1))

        print()

