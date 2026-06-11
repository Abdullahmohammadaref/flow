import networkx
from networkx.algorithms.components import strongly_connected_components


class GraphAnalyzer:
    def __init__(self, graph):
        self.graph = graph
        self.pagerank_scores = networkx.pagerank(self.graph, alpha=0.85)
        self.execution_order_counter = 1
        self.execution_order_visited_edges = set()

    def analyze_graph(self, train: bool = False):
        """
        Main method for calling relevant methods in correct order generate an analyzed graph.
        :return: an analyzed networkx graph
        """

        entry_nodes = self.detect_entry_points()

        # Don't analyze edges if we are just building a dataset
        if not train:
            self.initialize_edges_attributes()

            for entry_node in entry_nodes:
                self.mark_dependency_order(entry_node)
            for entry_node in entry_nodes:
                self.mark_node_execution_order(entry_node)

            self.detect_circular_dependencies()

        self.mark_node_pagerank_score()

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
        A depth first graph traversal algorithm to order edges based on runtime import execution order.
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
        Use strongly_connected_components to detect and lable circular imports
        """
        strongly_connected_components = []
        for i in networkx.strongly_connected_components(self.graph):
            if len(i) > 1:
                strongly_connected_components.append(i)

        cycle_count = 0
        for component in strongly_connected_components:
            nodes_in_cycle = []
            for node in component:
                if self.graph.nodes[node]['type'] == "LocalFile":
                    nodes_in_cycle.append(node)

            if len(nodes_in_cycle) >= 2:
                cycle_count += 1
                for node in nodes_in_cycle:
                    for neighbor in self.graph.neighbors(node):
                        if self.graph.neighbors(node):
                            self.graph.edges[node, neighbor]['has_circular_dependency'] = True

    def mark_node_pagerank_score(self):
        """
        Use networkx "pagerank" to give a score for each node that is based on how many files import this file
        """
        for node in self.graph.nodes:
            self.graph.nodes[node]['pagerank_score'] = self.pagerank_scores[node]


