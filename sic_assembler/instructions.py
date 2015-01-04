import json
from errors import LineFieldsError 

def get_dict():
	f = open('json_dict','r')
	return json.load(f)


op_table = get_dict()

registers_table = {'A': 0,
                   'X': 1,
                   'L': 2,
                   'PC': 8,
                   "SW": 9
                  }

#indexed addressing
indexed = lambda x: str(x).endswith(',X')

class SicFormat():
	"""sic format 
	8 1 15
	===================================
	|op      |x|        disp          |
	===================================
	"""
	def __init__(self,symtab,source_line):
		
		self._symtab = symtab
		self._line_number = source_line.line_number
		self._mnemonic = source_line.mnemonic
		self._location = None;
		self._disp = source_line.operand
		self._content = source_line
		
	def generate(self):
		"""generate the object code for the instruction"""
		if self._mnemonic is None:
			raise LineFieldsError(message = "mnemonic was not specified")
		
		output = ""
		#opcode
		opcode_lookup = str(op_table[self._mnemonic])
		
		if self._disp is not None:
			if indexed(self._disp):
				self._disp = self._disp[:len(self._disp)-2]
				symbol_address = self._symtab.get(self._disp)
				modified_symbol_address = int(str(symbol_address),16) + 32768
				symbol_address = str(hex(modified_symbol_address))[2:]
			else:
				symbol_address = self._symtab.get(self._content.operand)[2:]
		else:
			symbol_address = '0000'
			
		output = opcode_lookup + symbol_address
		hex_output = hex(int(str(output),16))[2:].zfill(6).upper()
			
		return self._mnemonic, self._disp, hex_output
				

def to_binary(hex_string):
	return bin(int(str(hex_string),16))[2:]
