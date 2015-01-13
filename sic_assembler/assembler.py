from record import generate_records
from instructions import op_table,SicFormat
from errors import DuplicateSymbolError,LineFieldsError,OpcodeLookupError
import codecs

# A Comment
comment = lambda x: x.split()[0].startswith('.')
#A Blank line
blank_line = lambda x: len(x.split()) == 0

#Remove commenrs from a line
def remove_comments(line):
	"""
	Search for a string in a line beginning with '.' and then return the list containing elements before comment
	"""
	for x,y in enumerate(line):
		if comment(y):
			return line[:x]
	return line

class SourceLine(object):
	def __init__(self,line_number, label, mnemonic, operand):
		self.location = None
		self.line_number = line_number
		self.label = label
		self.mnemonic = mnemonic
		self.operand = operand
	
	@staticmethod
	def parse(line, line_number):
		"""
		parse an individual line and returns a SourceLine object
		"""
		fields = remove_comments(line.split())
		#if there is a space between 2 operand like buffer, x or buffer ,x then we fix that to buffer,x
		if len(fields) > 1 and fields[1].endswith(','):
			operand = fields.pop(1) + fields.pop(1)
			fields.append(operand)
		elif len(fields) > 2 and fields[2].endswith(','):
			operand = fields.pop(2) + fields.pop(2)
			fields.append(operand)
		
		if len(fields) is 3:
			return SourceLine( label = fields[0], mnemonic = fields[1], operand = fields[2], line_number = line_number)
		elif len(fields) is 2:
			return SourceLine( label = None, mnemonic = fields[0], operand = fields[1], line_number = line_number)
		elif len(fields) is 1:
			return SourceLine( label = None, mnemonic = fields[0], operand = None, line_number = line_number)
		elif len(fields) > 3 and line.strip().endswith("'"):
			line = line.strip()
			index = line.find("C'")
			fields[2] = line[index:]
			return SourceLine( label = fields[0], mnemonic = fields[1], operand = fields[2], line_number = line_number)
		else:
			raise LineFieldsError( message = 'Invalid amounts of fields on line' + str(line_number + 1))
			
	def __repr__(self):
		return "<SourceLine %s %s %s >" % (self.label,self.mnemonic,self.operand)

class Assembler(object):
	def __init__(self, inputfile ):

		# a generator to iterate over file lines
		self.contents = (line.strip('\n') for line in inputfile.readlines())
		
		# A temporary array to hold result of the first pass
		self.temp_contents = []
		#Symbol table
		self.symtab = dict()
		#location counter
		self.locctr = int(0)
		#start address
		self.start_address = 0
		#program length
		self.program_length = 0
		#program name
		self.program_name = ""
		#array of tuples containing debugging information
		self.__generated_objects = []
		#array of the generated records
		self.__generated_records = []
		
	def assemble(self):
		"""assemble the contents of file object"""
		if len(self.__generated_records) is 0:
			self.first_pass()
			self.second_pass()
			#generate some records
			self.__generated_records = self.generate_records()
			
		return self.generated_records
	
	def first_pass(self):
		""" 1st pass """
		
		#To check for start opcode in 1st line
		first = next(self.contents)
		first_line = SourceLine.parse(first , line_number=1 )
		
		if first_line.mnemonic is not None:
			#if the opcode is start set the locctr to startiing address
			if first_line.mnemonic == 'START':
				self.start_address = int(first_line.operand,16)
				self.locctr = int(first_line.operand,16)
				self.program_name = first_line.label
				
		#loop through all the lines except first
		for line_number , line in enumerate(self.contents):
			print line,hex(self.locctr)
			if not blank_line(line) and not comment(line):
				source_line = SourceLine.parse(line, line_number)
				source_line.location = self.locctr
				
				# search for the label if present in the line,add it to symtab
				if source_line.label is not None:
					if source_line.label not in self.symtab:
						self.symtab[source_line.label] = hex(int(self.locctr))
					else:
						raise DuplicateSymbolError(message = "A Duplicate symbol was found on the line: " + str(line_number+2))
				
				#search optab for the mnemonic
				mnemonic = source_line.mnemonic
				if mnemonic in op_table:
					self.locctr += 3
				elif mnemonic == 'WORD':
					self.locctr += 3
				elif mnemonic == 'RESW':
					self.locctr += 3 * int(source_line.operand)
				elif mnemonic == 'RESB':
					self.locctr += int(source_line.operand)
				elif mnemonic == 'BYTE':
					if source_line.operand.startswith('X'):
						value = source_line.operand.replace("X",'')
						stripped_value = value.replace("'",'')
						#hex_value = int(stripped_value,16)
						self.locctr += (len(stripped_value))/2
					elif source_line.operand.startswith('C'):
						value = source_line.operand.replace("C",'')
						stripped_value = value.replace("'",'')
						self.locctr += len(stripped_value)
					else:
						raise LineFieldsError(message = "Invalid Byte for line" + str(line_number+2))
				#if encountered END then break the first pass
				elif mnemonic == 'END':
					break
				else:
					raise OpcodeLookupError(message = 'The mnemonic is invalid on line: ' + str(line_number + 2))
				
				self.temp_contents.append(source_line)

	def second_pass(self):
		"""2nd pass"""
		
		object_code = []
		
		for source_line in self.temp_contents:
			found_opcode = op_table.get(source_line.mnemonic)
			if found_opcode:
				instruction = SicFormat( symtab = self.symtab, source_line = source_line )
				instruction_output = instruction.generate()
				object_code.append((source_line.location,instruction_output))
			else:
				if source_line.mnemonic == 'WORD':
					hex_value = hex(int(source_line.operand))
					stripped_value = hex_value.lstrip("0x")
					padded_value = stripped_value.zfill(6)
					object_info = (source_line.mnemonic, source_line.operand, padded_value )
					object_code.append((source_line.location,object_info))
				elif source_line.mnemonic == 'BYTE':
					if source_line.operand.startswith('X'):
						value = source_line.operand.replace("X",'')
						stripped_value = value.replace("'",'')
						object_info = (source_line.mnemonic,source_line.operand,stripped_value)
						object_code.append((source_line.location, object_info))
					elif source_line.operand.startswith("C"):
						value = source_line.operand.replace("C",'')
						stripped_value = value.replace("'",'')
						hex_value = codecs.encode(stripped_value,"hex").upper()
						object_info = (source_line.mnemonic,source_line.operand,hex_value)
						object_code.append((source_line.location,object_info))
					
						
		self.__generated_objects = object_code
		#print self.symtab
		#print op_table
		#for x,(a,b,c) in object_code:
		#	print hex(x),a,b,c
		#print object_code


	def generate_records(self):
		if len(self.__generated_records) > 0:
			return self.generated_records
		self.program_length = (self.locctr - self.start_address )
		self.__generated_records = generate_records(generated_objects = self.generated_objects, program_name = self.program_name, start_address = self.start_address, program_length = self.program_length )
		return self.generated_records

	@property
	def generated_objects(self):
		return self.__generated_objects
	
	@property
	def generated_records(self):
		return self.__generated_records
	

if __name__ == '__main__':
	a = Assembler(open('input','r'))
	g = a.assemble()
	for record in g:
		print record
