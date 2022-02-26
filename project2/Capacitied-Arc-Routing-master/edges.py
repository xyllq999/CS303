#!/usr/bin/python


class Edge:
    """The class defining a directed edge."""

    def __init__(self, source, target, cost=1, demand=0):
        """Load up a directed edge instance.
        
        Parameters
        ----------
        source : starting node
        target : ending node
        cost : number, optional (default=1)
        """
        self.source = source
        self.target = target
        self.cost = cost
        self.demand = demand

    def __repr__(self):
        """Compute the string representation of the edge."""
        if self.cost == 1:
            return "%s(%s, %s)" % (
                self.__class__.__name__,
                repr(self.source),
                repr(self.target))
        else:
            return "%s(%s, %s, %s, %s)" % (
                self.__class__.__name__,
                repr(self.source),
                repr(self.target),
                repr(self.cost),
                repr(self.demand))

    def __cmp__(self, other):
        """Comparing of edges (the cost first)."""
        # Check costs.
        if self.cost > other.cost:
            return 1
        if self.cost < other.cost:
            return -1
        # Check the first node.
        if self.source > other.source:
            return 1
        if self.source < other.source:
            return -1
        # Check the second node.
        if self.target > other.target:
            return 1
        if self.target < other.target:
            return -1
        return 0

    def __hash__(self):
        """Hashable edges."""
        # return hash(repr(self))
        return hash((self.source, self.target, self.cost, self.demand))

    def __invert__(self):
        """Return the edge with the opposite direction."""
        return self.__class__(self.target, self.source, self.cost, self.demand)

    inverted = __invert__


class UndirectedEdge(Edge):
    """The class defining an undirected edge."""

    def __init__(self, source, target, cost=1):
        """Load up an edge instance."""
        if source > target:
            self.source = target
            self.target = source
        else:
            self.source = source
            self.target = target
        self.cost = cost

    def __invert__(self):
        """The edge direction is not defined."""
        return self

# EOF
