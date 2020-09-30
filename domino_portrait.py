
from collections import deque

def create_costs(l):
    costs = {} 
    total_nodes = len(l) + len(l[0]) #assume all sublists have same length

    #for i in range(len(l)):
        #for j in range(len(l),total_nodes):
            #costs[(i,j)] = l[i][i]

    for i in range(len(l)):
        for j in range(len(l[i])):
            costs[(i,j + len(l))] = l[i][j]
    return costs
    
def graph_neighbours(graph,node):
    total_nodes = len(graph) + len(graph[0])
    seperator = len(graph)
    if node < seperator:
        return list(range(seperator,total_nodes))
    else:
        return list(range(seperator))

        
def get_path(pred,node):
    l = []
    curr = node
    while curr != -1:
        l.append(curr)
        curr = pred[curr]
    l.reverse() # or not
    res = []
    for i in range(len(l)-1):
        res.append((l[i],l[i+1]))
    return res



def bfs(graph,node,costs,prices,matching):
    total_nodes = len(graph) + len(graph[0])
    q = deque() 
    visited = list([False] * (total_nodes))
    inqueue = list([False] * (total_nodes))
    pred = list([-1] * (total_nodes))
    odd_nodes = set() 
    even_nodes = set() 
    for i in range(total_nodes):
        visited[i] = False
        inqueue[i] = False
        pred[i] =  -1

    q.append(node)
    inqueue[node] = True 
    q.append(-1)
    level = 0
    while len(q) > 1:
        c = q.popleft()
        if c == -1:
            level += 1 
            c = q.popleft()
            q.append(-1)
        inqueue[c] = True
        visited[c] = True
        if level % 2 == 0:
            next_level_odd = True
            even_nodes.add(c)
        else:
            next_level_odd = False
            odd_nodes.add(c)
        for u in graph_neighbours(graph,c):
            if not visited[u] and costs[(min(u,c),max(u,c))] == prices[u] + prices[c]:
                if next_level_odd and matching[u] is None:
                    pred[u] = c
                    path = get_path(pred,u)
                    #print(path,pred)
                    return path,odd_nodes,even_nodes
                if (next_level_odd and matching[c] is not None) or (not next_level_odd and matching[c] == u) and not inqueue[u]:
                    q.append(u)
                    inqueue[u] = True
                    pred[u] = c

    return None,odd_nodes,even_nodes


def hungarian(graph,costs):
    total_nodes = len(graph) + len(graph[0])
    matching = list([None] * total_nodes)
    prices = list([0] * total_nodes)
    while not is_perfect_matching(graph,matching):
        node =  find_first_unmatched(matching)
        path, odd_nodes, even_nodes = bfs(graph,node,costs,prices,matching)
        if path is not None:
            new_matching = matching[:]
            for u,v in path:
                new_matching[u] = v
                new_matching[v] = u
            matching = new_matching
            #print(matching)
        else:
            #print(odd_nodes,even_nodes)
            d = compute_delta(graph,odd_nodes,even_nodes,costs,prices)
            print(d)
            for u in even_nodes:
                prices[u] += d
            for u in odd_nodes:
                prices[u] -= d
    

def is_perfect_matching(graph,matching):
    print(matching)
    def truthy(e):
        return e is not None
    return all(map(truthy,matching))

def find_first_unmatched(matching):
    for i in range(len(matching)):
        if matching[i] is None:
            return i

def compute_delta(graph,odd_nodes,even_nodes,costs,prices):
    total_nodes = len(graph) + len(graph[0])
    all_nodes = set(list(range(total_nodes)))
    not_odd = all_nodes.difference(odd_nodes)
    l = []
    for u in list(even_nodes):
        for v in list(not_odd):
            key = (min(u,v),max(u,v))
            if key in costs:
                #print(costs[key])
                l.append(costs[key] - (prices[u] + prices[v]))
    
    return min(l)
        




l = [
    [1,1,2,43254],
    [3,4,5,32143],
    [6,7,8,43],
    [32,432,434],
    
]

#print(graph_neighbours(l,4))

print(create_costs(l).values())
print(hungarian(l,create_costs(l)))
