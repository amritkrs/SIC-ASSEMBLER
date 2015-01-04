import json
d = {}
with open("SIC_OPCODE") as f:
	for line in f:
		(key,val) = line.split()
		d[key] = val


f = open('json_dict','w')
json.dump(d,f)


