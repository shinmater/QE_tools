from ase import io
import sys

if len(sys.argv) ==1:
    sys.argv=['test','input.scf','test.xsf']

input_filename=sys.argv[1]
output_filename=sys.argv[2]

input_extension=input_filename.split('.')[-1]
output_extension=output_filename.split('.')[-1]
list_not_QE = ['vasp', 'xsf', 'cif']

if input_extension not in list_not_QE:
	input_format='espresso-in'
else:
	input_format=input_extension

if output_extension not in list_not_QE:
	output_format='espresso-in'
else:
	output_format=output_extension

ase_structure=io.read(input_filename,format=input_format)
io.write(output_filename, ase_structure, format=output_format)

from ase import spacegroup
sg_info = spacegroup.get_spacegroup(ase_structure)
print(sg_info)