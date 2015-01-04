from instructions import SicFormat

def generate_records(generated_objects, program_name, start_address, program_length):
	""" Generate a list of records """
	
	records = []
	
	header = gen_header( program_name, start_address, program_length )
	records.append(header)
	
	text = gen_text( generated_objects )
	for record in text:
		records.append(record)
	
	end = gen_end( start_address )
	records.append( end )
	
	return records

def gen_header( program_name, start_address, program_length ):
	""" Generate a Header Record """
	
	#specify the size of each column
	col2_size, col3_size, col4_size = 6,6,6
	
	col1 = "H"
	col2 = program_name[:col2_size].ljust(col2_size).upper()
	col3 = hex(start_address)[2:].zfill(col3_size).upper()
	col4 = hex(program_length)[2:].zfill(col4_size).upper()
	
	return col1 +col2 + col3 + col4

def gen_text( generated_code ):
	""" Generate a text record """
	
	code = list(generated_code) # create a copy of the code
	#specify the size of each column
	col2_size,col3_size,col4_size = 6,2,60
	
	generated_lines = []  #contains the temp_line of text records
	
	temp_line = [] #stores each line of text record
	temp_start_address = None #starting address of each text reocrds
	temp_line_length = 0 #length of text reocrds
	
	while len(code) > 0:
		col4 = ""
		
		while(len(col4) + len(code[0][1]) <= col4_size ):
			
			if (len(col4) + len(code[0][1][2]) ) > col4_size:
				break
			x = code.pop(0)
			temp_locctr = x[0]
			
			temp_contents = x[1][2]
			
			if temp_start_address is None:
				temp_start_address = x[0]
			
			temp_line_length += len(temp_contents)/2
			col4 = col4 + temp_contents
			
			if len(code) is 0:
				break
			if code[0][0] - temp_locctr > 3:
				break	
		
		temp_start_address = hex(temp_start_address)[2:].zfill(col2_size).upper()
		temp_line_length = hex(temp_line_length)[2:].zfill(col3_size).upper()
		temp_line = "T%s%s%s" % (temp_start_address, temp_line_length, col4)
		generated_lines.append(temp_line)
		
		temp_start_address = None
		temp_contents = []
		temp_line_length = 0
		
	return generated_lines


def gen_end( first_instruction_address ):
	"""generate end record"""
	
	col2_size = 6
	
	col1 = "E"
	col2 = hex(first_instruction_address)[2:].zfill(col2_size).upper()
	
	return col1 + col2

	
			
	
	
	
	
	
