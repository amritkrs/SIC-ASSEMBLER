import json
f = open('json_dict','r')
optab = json.load(f)
input = raw_input("Enter a line of sic code")
[opcode,address] = input.split()
print(optab[opcode] + address)
