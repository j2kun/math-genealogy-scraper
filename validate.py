''' validate data.json '''
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

for (source, target) in edges:
    if source not in nodes:
        print("Edge ({}, {}) is missing source".format(source, target))
    if target not in nodes:
        print("Edge ({}, {}) is missing target".format(source, target))
