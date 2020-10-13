import argparse
import sys
from collections import deque

def minc(matrix):
    return min(min([-1 * n for n in ll]) for ll in matrix) * -1

def create_graph(matrix,find_min,assignment): 
    graph = {}
    costs = {}
    rows = len(matrix)
    cols = len(matrix[0])   #assume all sublists have same length
    mincc = minc(matrix)
    def get_cost(val):
        if find_min:
            return val
        else:
            return -1 * val + mincc
    #first case
    if assignment:
        for i in range(rows + cols):
            if i < rows:
                graph[i] = list(range(rows,rows + cols))
                for j in range(cols):
                    costs[(i,j + rows)] = get_cost(matrix[i][j])
            else:
                graph[i] = list(range(rows))

    #second case:
    else:
        def out_of_bounds(point):
            x, y = point
            if x >= rows or x < 0:
                return False 
            if y >= cols or y < 0:
                return False
            return True
            
        
        def convert_one_dim(point):
            return point[0] * cols + point[1]
        
        for x in range(rows):
            for y in range(cols):
                node = convert_one_dim((x,y))
                neigh = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
                filtered_neigh = list(filter(out_of_bounds,neigh))
                graph[node] = list(map(convert_one_dim,filtered_neigh))
                for point in filtered_neigh:
                    if not point in costs:
                        n = convert_one_dim(point)
                        key = (min(n,node),max(n,node))
                        xx,yy = point
                        costs[key] = get_cost((matrix[xx][yy] - matrix[x][y]) ** 2)

    return graph,costs

def create_matrix_second_phase(matrix,matching_first_phase,lighting,dominoes):
    ret = [[j for j in range(330)] for i in range(330)] #init in 2d
    for i in range(330):
        for j in range(330):
            ret[i][j] = min((lighting[i][0] - dominoes[j][0]) ** 2 + (lighting[i][1] - dominoes[j][1]) ** 2,(lighting[i][0] - dominoes[j][1]) ** 2 + (lighting[i][1] - dominoes[j][0]) ** 2)
    return ret






def get_path(pred,node):
    l = []
    curr = node
    while curr != -1:
        l.append(curr)
        curr = pred[curr]
    l.reverse()
    res = []
    for i in range(len(l)-1):
        res.append((l[i],l[i+1]))
    return res



def bfs(graph,node,costs,prices,matching):
    total_nodes = len(graph.keys())
    q = deque() 
    visited = list([False] * (total_nodes))
    inqueue = list([False] * (total_nodes))
    pred = list([-1] * (total_nodes))
    odd_nodes = set() 
    even_nodes = set() 
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
        for u in graph[c]:
            if not visited[u] and costs[(min(u,c),max(u,c))] == prices[u] + prices[c]:
                if next_level_odd and matching[u] is None:
                    pred[u] = c
                    path = get_path(pred,u)
                    return path,odd_nodes,even_nodes
                if ((next_level_odd and matching[c] != u) or (not next_level_odd and matching[c] == u)) and not inqueue[u]:
                    q.append(u)
                    inqueue[u] = True
                    pred[u] = c

    return None,odd_nodes,even_nodes


def hungarian(graph,costs,assignment,find_min,matrix):
    total_nodes = len(graph.keys())
    matching = list([None] * total_nodes)
    prices = list([0] * total_nodes)
    while not is_perfect_matching(matching):
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
        else:
            d = compute_delta(graph,odd_nodes,even_nodes,costs,prices)
            for u in even_nodes:
                prices[u] += d
            for u in odd_nodes:
                prices[u] -= d
    cost = find_total_cost(graph,matching,costs,find_min,matrix)
    if assignment:
        return matching,cost
    else:
        tiles_match = format_matching_portrait1(graph,matching,costs,matrix)
        lighting = [(matrix[t1[0]][t1[1]],matrix[t2[0]][t2[1]]) for t1,t2 in tiles_match]
        dominoes = []
        for i in range(10):
            for j in range(i,10):
                for _ in range(6):
                    dominoes.append((i,j))
        msp = create_matrix_second_phase(matrix,tiles_match,lighting,dominoes)
        find_min2 = True
        assignment2 = True
        graph2,costs2 = create_graph(msp,find_min2,assignment2)
        dom_match, dom_cost = hungarian(graph2,costs2,assignment2, find_min2,msp)
        dom_match = format_matching_portrait2(dom_match,tiles_match,dominoes)
        return (tiles_match,dom_match),(cost,dom_cost)

    
def format_matching(graph,matching):
    stop = max(graph[max(graph.keys())]) + 1 #hacky 
    return [matching[i] - stop for i in range(stop)]


def find_total_cost(graph,matching,costs,find_min,matrix):
    l = unique_matching(matching)
    #print(l)
    if find_min:
        l = [costs[pair] for pair in l]
    else:
        l = [costs[pair] * -1 + minc(matrix) for pair in l]
    return sum(l,0)

def format_matching_portrait1(graph,matching,costs,matrix):
    def convert_two_dim(node):
        cols = len(matrix[0])
        x = node // cols
        y = node % cols
        return x,y
    def f(pair):
        return convert_two_dim(pair[0]),convert_two_dim(pair[1])
    l = unique_matching(matching)
    return list(map(f,l))

def format_matching_portrait2(matching,tiles,dominoes):
    l = unique_matching(matching)
    def f(pair):
        return (tiles[pair[0]],dominoes[pair[1] - 330])
    return list(map(f,l))

def unique_matching(matching):
    l = []
    for i in range(len(matching)):
        l.append((min(i,matching[i]),max(i,matching[i])))
    return list(dict.fromkeys(l))

def is_perfect_matching(matching):
    def truthy(e):
        return e is not None
    return all(map(truthy,matching))

def find_first_unmatched(matching):
    for i in range(len(matching)):
        if matching[i] is None:
            return i

def compute_delta(graph,odd_nodes,even_nodes,costs,prices):
    total_nodes = len(graph.keys())
    all_nodes = set(list(range(total_nodes)))
    not_odd = all_nodes.difference(odd_nodes)
    l = []
    for u in list(even_nodes):
        for v in list(not_odd):
            key = (min(u,v),max(u,v))
            if key in costs:
                l.append(costs[key] - (prices[u] + prices[v]))
    
    return min(l)
        




parser = argparse.ArgumentParser()
parser.add_argument('input_file',nargs = '?')
parser.add_argument("-m","--maximize",action="store_true",)
parser.add_argument("-a","--assignment",type=str)
parser.add_argument('tiling_file',nargs = '?')
parser.add_argument('dominoes_file',nargs = '?')
args = parser.parse_args()

inputf = args.input_file
assignment = False
find_min = False
if args.input_file is None:
    inputf = args.assignment
    assignment = True
    find_min = not args.maximize
with open(inputf) as f:
    matrix = f.readlines()
    matrix = [list(map(int,s.rstrip().split()))  for s in matrix]

graph, costs = create_graph(matrix,find_min,assignment)
matching, cost = hungarian(graph,costs,assignment,find_min,matrix)

def stringify_int_tuple(t):
    t = tuple(map(str,t))
    return '(' + t[0] + ', ' + t[1] + ')'

def tuplefy_str(s1,s2):
    return '('  + s1 + ', ' + s2 + ') '


if not assignment:
    tiles = ""
    tiles_matching = matching[0]
    dominoes_matching = matching[1]
    for pairs in tiles_matching:
        p1,p2 = pairs
        tiles += stringify_int_tuple(p1)  + ' ' + stringify_int_tuple(p2) + ' \n'
    
    dominoes = ""
    for pairs in dominoes_matching:
        p1 , p2 = pairs 
        dominoes += tuplefy_str(stringify_int_tuple(p1[0]),stringify_int_tuple(p1[1])) + ': ' + stringify_int_tuple(p2) + '\n'

    with open(args.tiling_file,'w+') as f:
        f.write(tiles)

    with open(args.dominoes_file,'w+') as f:
        f.write(dominoes)
    print(cost[0])
    print(cost[1])
else:
    fmatching = format_matching(graph,matching)
    for n in fmatching:
        print(n,end=' ')
    print()
    print(cost)
