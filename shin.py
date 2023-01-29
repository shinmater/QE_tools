from ase import io
import sys

#input_filename=sys.argv[1]
#output_filename=sys.argv[2]

input_filename='vasp_test.scf'
output_filename = 'test.vasp'

input_extension=input_filename.split('.')[-1]
output_extension=output_filename.split('.')[-1]

if input_extension == 'in':
	input_format='espresso-in'
else:
	input_format=input_extension

if output_extension == 'in':
	output_format='espresso-in'
else:
	output_format=output_extension

ase_structure=io.read(input_filename,format=input_format)
io.write(output_filename, ase_structure, format=output_format)

from ase import spacegroup
sg_info = spacegroup.get_spacegroup(ase_structure)
print(sg_info)