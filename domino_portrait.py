#TODO: create regular graph (dict like) to unify portrait cases and cost list case.

import argparse
import sys
from collections import deque

def create_costs(l,find_min):
    if len(l) != len(l[0]):
        print('cost array is not n x n')
        exit()
    costs = {} 
    total_nodes = len(l) + len(l[0]) #assume all sublists have same length

    #for i in range(len(l)):
        #for j in range(len(l),total_nodes):
            #costs[(i,j)] = l[i][i]

    minc = min(min([-1 * n for n in ll]) for ll in l)
    for i in range(len(l)):
        for j in range(len(l[i])):
            if find_min:
                costs[(i,j + len(l))] = l[i][j] 
            else:
                costs[(i,j + len(l))] = -1 * l[i][j] + minc
    #costs[(3,7)] = 55
    return costs

def create_graph(matrix): 
    graph = {}
    rows = len(matrix)
    cols = len(matrix[0])   #assume all sublists have same length
    for i in range(rows + cols):
        if i < rows:
            graph[i] = matrix[i]
        else:
            graph[i] = [l[i - rows] for l in matrix]

    


    #second case:



    pass
    
def graph_neighbours(graph,node):
    total_nodes = len(graph) + len(graph[0])
    seperator = len(graph)
    if node < seperator:
        return list(range(seperator,total_nodes))
    else:
        return list(range(seperator))


def graph_neighbours_portrait(graph,node):
    xlen = len(graph)
    ylen = len(graph[0])
    def out_of_bounds(point):
        x, y = point
        if x >= xlen or x < 0:
            return False 
        if y >= ylen or y < 0:
            return False
        return True
        
    def convert_two_dim(node):
        x = node // ylen
        y = node % ylen
        return x,y
    
    x, y = convert_two_dim(node)
    neigh = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
    return filter(neigh,out_of_bounds)
        
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
                if ((next_level_odd and matching[c] != u) or (not next_level_odd and matching[c] == u)) and not inqueue[u]:
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
            flag = True
            for u,v in path:
                if flag: 
                    new_matching[u] = v
                    new_matching[v] = u
                flag = not flag
            matching = new_matching
            #print(matching)
        else:
            #print(odd_nodes,even_nodes)
            d = compute_delta(graph,odd_nodes,even_nodes,costs,prices)
            #print(d)
            for u in even_nodes:
                prices[u] += d
            for u in odd_nodes:
                prices[u] -= d
    fmatching = format_matching(graph,matching)
    return fmatching,find_total_cost(graph,fmatching)

    

def format_matching(graph,matching):
    stop = len(graph)
    return [matching[i] - stop for i in range(stop)]


def find_total_cost(graph,fmatch):
    summ = 0
    for i in range(len(fmatch)):
        summ +=  graph[i][fmatch[i]]
    return summ




def is_perfect_matching(graph,matching):
    #print(matching)
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
                #print(costs[key],prices[u],prices[v])
                l.append(costs[key] - (prices[u] + prices[v]))
    
    #print(l)
    return min(l)
        




l = [
    [1,1,2,43254],
    [3,4,5,32143],
    [6,7,8,43],
    [32,432,434,231],
    
]

l3 = [
    [6, 2, 1, 9, 4,],
    [2, 9, 1, 8, 0,],
    [5, 9, 4, 7, 3,],
    [2, 9, 7, 0, 4,],
    [2, 3, 1, 4, 5,],
]

l2 = [
    [5,1,3],
    [3,0,5],
    [3,2,2],
]


l4 = [
    [3, 4, 3, 5, 4, 7, 0, 4, 4, 8],
    [8, 0, 6, 2, 2, 4, 8, 5, 6, 1],
    [3, 9, 8, 8, 6, 1, 1, 3, 6, 0],
    [5, 1, 2, 6, 5, 5, 1, 5, 3, 4],
    [8, 2, 9, 3, 6, 1, 2, 2, 0, 3],
    [1, 7, 8, 1, 4, 3, 9, 0, 0, 9],
    [0, 6, 8, 7, 6, 2, 1, 5, 3, 5],
    [9, 8, 4, 1, 2, 0, 6, 4, 9, 6],
    [7, 6, 7, 4, 6, 7, 3, 1, 4, 5],
    [7, 7, 5, 1, 2, 2, 8, 2, 9, 9 ],
]
#print(graph_neighbours(l,4))

parser = argparse.ArgumentParser()
parser.add_argument("-m","--maximize",action="store_false",)
parser.add_argument("-a","--assignment",type=str)
args = parser.parse_args()

if args.assignment:
    with open(args.assignment) as f:
        l = f.readlines()
        l = [list(map(int,s.rstrip().split()))  for s in l]

print(hungarian(l,create_costs(l,args.maximize)))
#print(hungarian(l4,create_costs(l4,False)))
#print(hungarian(l3,create_costs(l3,True)))
#print(hungarian(l,create_costs(l)))