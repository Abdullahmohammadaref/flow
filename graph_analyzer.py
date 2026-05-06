import networkx

class GraphAnalyzer:
    def __init__(self, graph):
        self.graph = graph
        self.execution_order_counter = 1
        self.execution_order_visited_edges = set()

    def analyze_graph(self):
        """
        Main method for calling relevant methods in correct order generate an analyzed graph.
        :return: an analyzed networkx graph
        """

        entry_nodes = self.detect_entry_points()
        self.initialize_edges_attributes()


        for entry_node in entry_nodes:
            self.mark_dependency_order(entry_node)


        for entry_node in entry_nodes:
            self.mark_node_execution_order(entry_node)


        self.detect_circular_dependencies()

        return self.graph

    def initialize_edges_attributes(self):
        for edge in self.graph.edges():
            self.graph.edges[edge]['dependency_order'] = None
            self.graph.edges[edge]['execution_order'] = None
            self.graph.edges[edge]['has_circular_dependency'] = False

    def detect_entry_points(self):
        """
        Put specified entry point nodes (like if __name__ == "__main__": nodes") in a list and detects unspecified entry points (like python packages)
        """
        entry_points = []

        for node in self.graph.nodes:
            if self.graph.nodes[node].get('is_entry_point') and self.graph.nodes[node]['type'] == "LocalFile":
                entry_points.append(node)

        # Fallback using in_degree incase code doesn't have entry point like a library or a disconnected code
        if not entry_points:
            for node in self.graph.nodes:
                if self.graph.in_degree(node) == 0 and self.graph.nodes[node]['type'] == "LocalFile":
                    entry_points.append(node)
        return entry_points

    def mark_node_execution_order(self, parent_node):
        """
        A depth first graph traversal algorithm to order edges based on runtime import-time execution order.
        :param: String name of a parent node
        """
        for child_node in sorted(self.graph.successors(parent_node)):
            edge = (parent_node, child_node)
            if edge not in self.execution_order_visited_edges:
                self.execution_order_visited_edges.add(edge)
                self.graph.edges[edge]['execution_order'] = self.execution_order_counter
                self.execution_order_counter += 1
                self.mark_node_execution_order(child_node)

    def mark_dependency_order(self, start_node):
        """
        A breadth first graph traversal algorithm to order edges based on their depth from the entry point.
        :param: String name of a parent node
        """
        queue = []
        visited_edges = set()

        queue.append((start_node, 1))

        while len(queue) > 0:
            parent_node, depth = queue.pop(0)

            for child_node in sorted(self.graph.successors(parent_node)):
                edge = (parent_node, child_node)
                if edge not in visited_edges:
                    visited_edges.add(edge)
                    self.graph.edges[edge]['dependency_order'] = depth
                    queue.append((child_node, depth + 1))

    def detect_circular_dependencies(self):
        """
        Use networkx "simple_cycles" to detect and lable circular imports
        """
        cycle_count = 0
        for cycle in networkx.simple_cycles(self.graph):
            nodes_in_cycle = []
            for node in cycle:
                if self.graph.nodes[node]['type'] == "LocalFile":
                    nodes_in_cycle.append(node)

            if len(nodes_in_cycle) >= 2:
                cycle_count += 1
                for i in range(len(nodes_in_cycle)):
                    source = nodes_in_cycle[i]
                    target = nodes_in_cycle[(i + 1) % len(nodes_in_cycle)]
                    if self.graph.has_edge(source, target):
                        self.graph.edges[source, target]['has_circular_dependency'] = True