class Node:
    def __init__(self, NodeA, NodeB, Weight):
        self.NodeA = NodeA
        self.NodeB = NodeB
        self.Weight = Weight
        self.next = None

class TrieNode:
    def __init__(self):
        self.children = {}
        self.counts = {}

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert_path(self, nodeA, nodeB):
        current = self.root
        if nodeA not in current.children:
            current.children[nodeA] = TrieNode()
        current = current.children[nodeA]
        if nodeB in current.counts:
            current.counts[nodeB] += 1
        else:
            current.counts[nodeB] = 1
    
    def suggest_destinations(self, nodeA):
        current = self.root
        if nodeA in current.children:
            current = current.children[nodeA]
            sorted_destinations = sorted(current.counts.items(), key=lambda x: x[1], reverse=True)
            return [node for node, _ in sorted_destinations]
        return []


class LinkedList:
    def __init__(self):
        self.head = None

    def insert_first(self, NodeA, NodeB, Weight):
        Temp = Node(NodeA, NodeB, Weight)
        if self.head == None:
            self.head = Temp
        else:
            Temp.next = self.head
            self.head = Temp

    def insert_last(self, NodeA, NodeB, Weight):
        Temp = self.head
        if self.head == None:
            self.head = Node(NodeA, NodeB, Weight)
        else:
            while (Temp.next!= None):
                Temp = Temp.next
            Temp.next = Node(NodeA, NodeB, Weight)

    def delete_first(self):
        self.head = self.head.next

    def delete_last(self):
        Temp = self.head
        if Temp.next == None:
            self.head = None
        else:
            while Temp.next.next!= None:
                Temp = Temp.next
            Temp.next = None

    def delete_node(self, NodeA, NodeB):
        Temp = self.head

        if Temp.NodeA == NodeA and Temp.NodeB == NodeB:
            self.delete_first()
            return

        while (Temp!= None and (Temp.NodeA == NodeA and Temp.NodeB == NodeB)):
            Temp = Temp.next

        if Temp == None:
            return
        else:
            Temp.next = Temp.next.next

    def delete_at_index(self, index):
        if self.head == None:
            return

        Temp = self.head
        position = 1
        if position == index:
            self.delete_first()
        else:
            while (Temp!= None and position + 1!= index):
                position = position + 1
                Temp = Temp.next

            if Temp!= None:
                Temp.next = Temp.next.next
            else:
                print("Index not present")

    def find_node(self, ind):
        Temp = self.head
        i = 1
        while (Temp!= None):
            if ind == i:
                Tempe = [Temp.NodeA, Temp.NodeB, Temp.Weight]
                return Tempe
            i += 1
            Temp = Temp.next
        else:
            return []

    def find_custom(self, NodeA, NodeB):
        Temp = self.head
        i = 1
        while (Temp!= None):
            if Temp.NodeA == NodeA and Temp.NodeB == NodeB:
                Tempe = [Temp.NodeA, Temp.NodeB, Temp.Weight]
                self.delete_at_index(i)
                return Tempe
            i += 1
            Temp = Temp.next
        else:
            return []

    def print_nodes(self, contd):
        if not contd:
            i = 5
        else:
            i = 1
        Temp = self.head
        while (Temp!= None):
            print(i, Temp.NodeA, '->', Temp.NodeB, Temp.Weight)
            i += 1
            Temp = Temp.next

    def length(self):
        Temp = self.head
        i = 0
        while (Temp!= None):
            i += 1
            Temp = Temp.next
        return i


class MinHeap:
    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def left(self, i):
        return 2 * i + 1

    def right(self, i):
        return 2 * i + 1

    def insertVal(self, val, Node):
        self.heap.append([val, Node])
        i = len(self.heap) - 1
        while i!= 0 and self.heap[i][0] < self.heap[self.parent(i)][0]:
            self.heap[i], self.heap[self.parent(i)] = self.heap[self.parent(i)], self.heap[i]
            i = self.parent(i)

    def decreaseVal(self, i, newVal):
        self.heap[i][0] = newVal
        while i!= 0 and self.heap[i][0] < self.heap[self.parent(i)][0]:
            self.heap[i], self.heap[self.parent(i)] = self.heap[self.parent(i)], self.heap[i]
            i = self.parent(i)

    def getMin(self):
        return self.heap[0]

    def extractMin(self):
        if len(self.heap) == 0:
            return -999

        if (len(self.heap) == 1):
            return self.heap.pop()

        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self.MinHeapify(0)
        return root

    def delete(self, i):
        self.decreaseVal(i, -999999)
        self.extractMin()

    def MinHeapify(self, i):
        l = self.left(i)
        r = self.right(i)

        smallest = i
        if l < len(self.heap) and self.heap[l][0] < self.heap[smallest][0]:
            smallest = l
        if r < len(self.heap) and self.heap[r][0] < self.heap[smallest][0]:
            smallest = r
        if smallest!= i:
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            self.MinHeapify(smallest)

    def increaseVal(self, i, newVal):
        self.heap[i][0] = newVal
        self.MinHeapify(i)

    def changeVal(self, i, newVal):
        if self.heap[i][0] == newVal:
            return
        if self.heap[i][0] < newVal:
            self.increaseVal(i, newVal)
        else:
            self.decreaseVal(i, newVal)


class Graph:
    def __init__(self):
        self.graph = {}
        self.toll_prices = {}  # To store toll prices for edges

    def add_edge_undirected(self, NodeA, NodeB, Weight):
        if NodeA not in self.graph:
            self.graph[NodeA] = []
        if NodeB not in self.graph:
            self.graph[NodeB] = []
        self.graph[NodeA].append([NodeB, Weight])
        self.graph[NodeB].append([NodeA, Weight])

    def update_graph_undirected(self, NodeA, NodeB, Weight):
        if NodeA in self.graph and NodeB in self.graph:
            for Node in self.graph[NodeA]:
                if Node[0] == NodeB:
                    Node[1] = Weight
                    break
            else:
                self.add_edge_undirected(NodeA, NodeB, Weight)
                return

            for Node in self.graph[NodeB]:
                if Node[0] == NodeA:
                    Node[1] = Weight

    def add_edge_directed(self, NodeA, NodeB, Weight, toll_price=0):
        if NodeA not in self.graph:
            self.graph[NodeA] = []
        self.graph[NodeA].append([NodeB, Weight])
        if NodeB not in self.graph:
            self.graph[NodeB] = []
        
        self.toll_prices[(NodeA, NodeB)] = toll_price

    def update_graph_directed(self, NodeA, NodeB, Weight):
        if NodeA in self.graph and NodeB in self.graph:
            for Node in self.graph[NodeA]:
                if Node[0] == NodeB:
                    Node[1] = Weight
                    break
            else:
                self.add_edge_directed(NodeA, NodeB, Weight)

    def display_graph(self):
        for Node in self.graph:
            print(Node, '->', self.graph[Node])

def shortest_path(graph, NodeA, NodeB):
    distances = {}
    for Node in graph:
        distances[Node] = float('inf')
    distances[NodeA] = 0
    Heap = MinHeap()
    Heap.insertVal(0, NodeA)
    previous_nodes = {}
    for Node in graph:
        previous_nodes[Node] = []

    while len(Heap.heap)!= 0:
        current_distance, Temp = Heap.extractMin()
        if Temp == NodeB:
            break
        for neighborNode, length in graph[Temp]:
            distance = current_distance + length
            if distance < distances[neighborNode]:
                distances[neighborNode] = distance
                previous_nodes[neighborNode] = [Temp]
                Heap.insertVal(distance, neighborNode)
            elif distance == distances[neighborNode]:
                previous_nodes[neighborNode].append(Temp)

    def backtrack_paths(current):
        if current == NodeA:
            return [[NodeA]]
        paths = set()
        for predecessor in previous_nodes[current]:
            for path in backtrack_paths(predecessor):
                paths.add(tuple(path + [current]))
        return [list(path) for path in paths]

    all_paths = backtrack_paths(NodeB)
    if distances[NodeB] == float('inf'):
        print('No Path')
    else:
        print('All shortest paths:', all_paths, 'of distance', distances[NodeB])

def prim_mst_traffic(graph, traffic_graph, start_node):
    mst = Graph()
    visited = set()
    visited.add(start_node)
    edges = []

    for neighbor, weight in graph[start_node]:
        edges.append((weight, start_node, neighbor))

    while edges:
        edges.sort()
        weight, node_a, node_b = edges.pop(0)
        if node_b not in visited:
            visited.add(node_b)
            mst.add_edge_directed(node_a, node_b, weight)
            for neighbor, neighbor_weight in graph[node_b]:
                if neighbor not in visited:
                    edges.append((neighbor_weight, node_b, neighbor))

    # Integrate traffic timings
    traffic_timings = allocate_traffic_timings(traffic_graph)
    for node in mst.graph:
        for neighbor, weight in mst.graph[node]:
            weight += traffic_timings.get(node, 0)
            mst.update_graph_directed(node, neighbor, weight)

    def dfs_path(current, target, path, total_weight, visited_path):
        if current == target:
            return path + [current], total_weight
        
        visited_path.add(current)
        for neighbor, weight in mst.graph.get(current, []):
            if neighbor not in visited_path:
                result = dfs_path(neighbor, target, path + [current], total_weight + weight, visited_path)
                if result:
                    return result  # Return as soon as the path is found
        return None, float('inf')

    # Find and return the path and weight from start_node to end_node
    path, total_weight = dfs_path(start_node, end_node, [], 0, set())
    return path, total_weight

def floyd_warshall_toll_free(graph, toll_graph, start_node, end_node):
    if not isinstance(graph, Graph):
        raise TypeError("Expected 'graph' to be an instance of the Graph class.")
    
    distances = {node: {node: float('inf') for node in graph.graph} for node in graph.graph}
    for node in graph.graph:
        distances[node][node] = 0
        for neighbor, weight in graph.graph[node]:
            distances[node][neighbor] = weight

    # Initialize tolls in the distance matrix
    for (node_a, node_b), toll_price in toll_graph.toll_prices.items():
        if node_a in distances and node_b in distances[node_a]:
            distances[node_a][node_b] += toll_price

    for intermediate in graph.graph:
        for start in graph.graph:
            for end in graph.graph:
                if distances[start][intermediate] + distances[intermediate][end] < distances[start][end]:
                    distances[start][end] = distances[start][intermediate] + distances[intermediate][end]

    # Return the shortest path and its distance
    toll_free_distance = distances[start_node][end_node]
    if toll_free_distance != float('inf'):
        toll_free_path = []
        current_node = end_node
        while current_node != start_node:
            toll_free_path.append(current_node)
            for neighbor, weight in graph.graph[current_node]:
                if distances[start_node][current_node] - weight == distances[start_node][neighbor]:
                    current_node = neighbor
                    break
        toll_free_path.append(start_node)
        toll_free_path.reverse()
        print(f'Toll-free distance: {toll_free_distance}, Path: {toll_free_path}')
    else:
        print('No toll-free path found.')

def allocate_traffic_timings(dir_graph):
    timings = {}
    for data in dir_graph:
        if len(dir_graph[data]) > 1:
            timings[data] = 0
            for nodes in dir_graph[data]:
                timings[data] += nodes[1]

                for nodes1 in dir_graph[nodes[0]]:
                    if nodes1[0] == data:
                        timings[data] += nodes1[1]
                        break
            timings[data] = int(timings[data] / 4)
    return timings

def find_shortest_path_with_tolls(graph, NodeA, NodeB):
    # Use graph.graph to access the underlying dictionary of nodes and edges
    distances = {node: float('inf') for node in graph.graph}
    distances[NodeA] = 0
    Heap = MinHeap()
    Heap.insertVal(0, NodeA)
    previous_nodes = {node: [] for node in graph.graph}

    while len(Heap.heap) != 0:
        current_distance, Temp = Heap.extractMin()
        if Temp == NodeB:
            break
        for neighborNode, length in graph.graph[Temp]:
            # Get the current toll for this edge
            toll_price = graph.toll_prices.get((Temp, neighborNode), 0) if hasattr(graph, 'toll_prices') else 0
            total_cost = current_distance + length + toll_price
            if total_cost < distances[neighborNode]:
                distances[neighborNode] = total_cost
                previous_nodes[neighborNode] = [Temp]
                Heap.insertVal(total_cost, neighborNode)
                
    return distances, previous_nodes

def find_the_path_with_least_tolls(graph, NodeA, NodeB):
    if NodeA not in graph.graph or NodeB not in graph.graph:
        print(f"One or both nodes do not exist in the graph: {NodeA}, {NodeB}.")
        return None, None  # Handle the error as appropriate

    distances = {Node: float('inf') for Node in graph.graph}
    distances[NodeA] = 0
    Heap = MinHeap()
    Heap.insertVal(0, NodeA)
    previous_nodes = {Node: [] for Node in graph.graph}

    while len(Heap.heap) != 0:
        current_distance, Temp = Heap.extractMin()
        
        # Check if Temp is valid in graph
        if Temp not in graph.graph:
            print(f"Error: Current node {Temp} not found in the graph.")
            continue
        
        if Temp == NodeB:
            break

        for neighborNode, length in graph.graph[Temp]:
            toll_price = graph.toll_prices.get((Temp, neighborNode), 0)
            total_cost = current_distance + length + toll_price
            if total_cost < distances[neighborNode]:
                distances[neighborNode] = total_cost
                previous_nodes[neighborNode] = [Temp]
                Heap.insertVal(total_cost, neighborNode)

    return distances, previous_nodes

def road_maintenance(graph, blocked_roads):
    def block_road(graph, blocked_roads):
        node_a = input("Node A: ")
        node_b = input("Node B: ")
        if node_a in graph.graph and node_b in graph.graph:
            for node in graph.graph[node_a]:
                if node[0] == node_b:
                    # Insert the blocked road into the linked list
                    blocked_roads.insert_last(node_a, node_b, node[1])
                    graph.graph[node_a].remove(node)  # Remove from graph
                    print("Path removed Successfully")
                    break
            else:
                print("Path not removed as entered path does not exist")
                return
        else:
            print("Invalid nodes provided.")

    def unblock_road(graph, blocked_roads):
        print(1, 'Unblock the lastly blocked road', blocked_roads.find_node(blocked_roads.length()))
        print(2, 'Unblock the earliest blocked road', blocked_roads.find_node(1))
        print(3, 'Unblock your desired road')
        print(4, 'Quit/Back')
        
        blocked_roads.print_nodes(True)  # Ensure this line is present to show all blocked roads

        ch = int(input())
        if ch == 1:
            blocked = blocked_roads.find_node(blocked_roads.length())
            if blocked:
                blocked_roads.delete_at_index(blocked_roads.length())
                graph.add_edge_undirected(blocked[0], blocked[1], blocked[2])  # Re-add to graph
                print("Last blocked road unblocked successfully.")
            else:
                print("No roads to unblock.")
        elif ch == 2:
            blocked = blocked_roads.find_node(1)
            if blocked:
                blocked_roads.delete_at_index(1)
                graph.add_edge_undirected(blocked[0], blocked[1], blocked[2])  # Re-add to graph
                print("First blocked road unblocked successfully.")
            else:
                print("No roads to unblock.")
        elif ch == 3:
            NodeA = input("Node A: ")
            NodeB = input("Node B: ")
            blocked = blocked_roads.find_custom(NodeA, NodeB)
            if blocked:
                graph.add_edge_undirected(blocked[0], blocked[1], blocked[2])  # Re-add to graph
                print("Custom road unblocked successfully.")
            else:
                print("No such road found in the block list.")
        elif ch == 4:
            print('Quitting')
            return
        else:
            print("Invalid input...Quitting..")

    ch = int(input("1: Block a Road\n2: Unblock a Road\n3: Show Blocked Roads"))

    if ch == 1:
        block_road(graph, blocked_roads)
    elif ch == 2:
        unblock_road(graph, blocked_roads)
    elif ch == 3:
        print("Blocked Roads:")
        blocked_roads.print_nodes(True)
    else:
        print("Invalid input...Quitting..")

if __name__ == "__main__":
    Road = Graph()
    Traffics = Graph()
    Toll = Graph()
    BlockedRoad = LinkedList()
    search_trie = Trie()
 

    ch = 99
    while ch!= 9:
        print("______________Welcome to Traffic Management______________")
        print()
        print()
        print(1, "Initialize Road Data")
        print(2, "Initialize Traffic Data")
        print(3, "Initialize Toll Data")
        print(4, "Find Shortest Path")
        print(5, "Find Shortest Path with traffic efficiency")
        print(6, "Find Toll-Free Shortest Paths")
        print(7, "Manage Roads")
        print(8, "See traffic light timings")
        print(9, "Quit")

        ch = int(input("Enter Your choice"))

        if ch == 1:
            cch = 0
            print(1, "Enter Road Data Manually")
            print(2, "Initialize existing Road ")
            print(3, "Return")
            cch = int(input("Enter your choice"))
            if cch == 2:
                Road = Graph()
                Road.add_edge_undirected('0', '1', 3)
                Road.add_edge_undirected('0', '3', 7)
                Road.add_edge_undirected('0', '4', 8)
                Road.add_edge_undirected('1', '3', 4)
                Road.add_edge_undirected('1', '2', 1)
                Road.add_edge_undirected('3', '2', 2)
                Road.add_edge_undirected('3', '4', 3)
                Road.add_edge_undirected('0', '2', 3)
                Road.display_graph()
            if cch == 1:
                Road=Graph()
                csch = 'y'
                while (csch == 'y'):
                    NodeA = input("Input First Node")
                    NodeB = input("Second Node")
                    Weight = int(input("Enter Weight"))
                    Road.add_edge_undirected(NodeA, NodeB, Weight)
                    csch = input('Continue?(y/n)')
            elif cch == 3:
                print("Returning")
        elif ch == 2:
            print(1, "Enter Traffic Data Manually")
            print(2, "Initialize existing Traffic")
            print(3, "Return")
            cch = int(input("Enter your choice"))
            if cch == 2:
                Traffics = Graph()
                Traffics.add_edge_directed('0', '1', 3)
                Traffics.add_edge_directed('1', '0', 2)
                Traffics.add_edge_directed('0', '3', 7)
                Traffics.add_edge_directed('3', '0', 5)
                Traffics.add_edge_directed('0', '4', 8)
                Traffics.add_edge_directed('4', '0', 6)
                Traffics.add_edge_directed('1', '3', 4)
                Traffics.add_edge_directed('3', '1', 2)
                Traffics.add_edge_directed('1', '2', 1)
                Traffics.add_edge_directed('2', '1', 3)
                Traffics.add_edge_directed('3', '2', 2)
                Traffics.add_edge_directed('2', '3', 4)
                Traffics.add_edge_directed('3', '4', 3)
                Traffics.add_edge_directed('4', '3', 5)
                Traffics.add_edge_directed('0', '2', 3)
                Traffics.add_edge_directed('2', '0', 3)
                Traffics.display_graph()


            if cch == 1:
                Road = Graph()
                csch = 'y'
                while (csch == 'y'):
                    NodeA = input("Input First Node")
                    NodeB = input("Second Node")
                    Weight = int(input("Enter Weight"))
                    Traffics.add_edge_directed(NodeA, NodeB, Weight)
                    csch = input('Continue?(y/n)')
            elif cch == 3:
                print("Returning")
        elif ch == 3:
            print(1, "Enter Toll Data Manually")
            print(2, "Initialize existing Toll")
            print(3, "Return")
            cch = int(input("Enter your choice"))
            if cch == 2:
                Toll = Graph()
                Toll.add_edge_undirected('0', '1', 5)
                Toll.add_edge_undirected('1', '0', 4)
                Toll.add_edge_undirected('0', '3', 6)
                Toll.add_edge_undirected('3', '0', 5)
                Toll.add_edge_undirected('0', '4', 7)
                Toll.add_edge_undirected('4', '0', 6)
                Toll.add_edge_undirected('1', '3', 8)
                Toll.add_edge_undirected('3', '1', 7)
                Toll.add_edge_undirected('1', '2', 2)
                Toll.add_edge_undirected('2', '1', 3)
                Toll.add_edge_undirected('3', '2', 4)
                Toll.add_edge_undirected('2', '3', 5)
                Toll.display_graph()
            if cch == 1:
                Road = Graph()
                csch = 'y'
                while (csch == 'y'):
                    NodeA = input("Input First Node")
                    NodeB = input("Second Node")
                    Weight = int(input("Enter Weight"))
                    Toll.add_edge_undirected(NodeA, NodeB, Weight)
                    csch = input('Continue?(y/n)')
            elif cch == 3:
                print("Returning")
        elif ch == 4:
            start_node = input("Enter start node: ")
            suggestions = search_trie.suggest_destinations(start_node)
            if suggestions:
                print("Suggested destinations based on frequently searched paths:")
                print(", ".join(suggestions))
            end_node = input("Enter end node: ")
            shortest_path(Road.graph, start_node, end_node)
            search_trie.insert_path(start_node, end_node)
        elif ch == 5:
            start_node = input("Enter start node: ")
            suggestions = search_trie.suggest_destinations(start_node)
            if suggestions:
                print("Suggested destinations based on frequently searched paths:")
                print(", ".join(suggestions))
            end_node = input("Enter end node: ")
            print(prim_mst_traffic(Road.graph, Traffics.graph, start_node))
            search_trie.insert_path(start_node, end_node)
        elif ch == 6:
            start_node = input("Enter start node: ")
            suggestions = search_trie.suggest_destinations(start_node)
            if suggestions:
                print("Suggested destinations based on frequently searched paths:")
                print(", ".join(suggestions))
            end_node = input("Enter end node: ")
            search_trie.insert_path(start_node, end_node)
            toll_free_distance, toll_free_path = floyd_warshall_toll_free(Road, Toll, start_node, end_node)
           
        elif ch == 7:
            road_maintenance(Road, BlockedRoad)
        elif ch == 8:
            start_node = input("Enter Node to see Signal timings")
            timings=allocate_traffic_timings(Traffics.graph)
            if start_node in timings:
                print(timings[start_node])
            else:
                print('No Signal Allocation for this node')
        elif ch == 9:
            print("Exiting the program.")
        else:
            print("Invalid choice. Please try again.")