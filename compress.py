''' Compress data.json for planned use with d3 '''
import json


with open('data.json', 'r') as infile:
    data = json.load(infile)

nodes = dict()
edges = []


for record in data['nodes']:
    _id = record['id']
    nodes[_id] = record['name']
    for student in record['students']:
        edges.append((_id, student))
    for advisor in record['advisors']:
        edges.append((advisor, _id))


edges = [list(x) for x in sorted(list(set(edges)))]
compressed = {
    'nodes': nodes,
    'edges': edges,
}

with open('genealogy_graph.json', 'w') as outfile:
    json.dump(compressed, outfile)
