from pymatgen.core import Structure
from ase import io
import os
import sys
from pymatgen.io.pwscf import PWInput

if len(sys.argv) ==1:
    sys.argv=['test','test.vasp','test.xsf']

input_filename=sys.argv[1]
output_filename=sys.argv[2]

input_extension=input_filename.split('.')[-1]
output_extension=output_filename.split('.')[-1]
list_not_QE = ['vasp', 'xsf', 'cif']

#qe_bulk = PWInput.from_file('bulk.in')

flag_delete_file = False
if input_extension not in list_not_QE:
    input_format='espresso-in'
    ase_structure=io.read(input_filename,format=input_format)
    io.write('struct_convert_temporary.vasp', ase_structure, format='vasp')
    struct = Structure.from_file('struct_convert_temporary.vasp')
    flag_delete_file = True
    # temp_open = open(input_filename, 'r')
    # lines = temp_open.readlines()
    # string_to_read = ''
    # for line in lines:
    #     if 'CELL_PARAMETERS' in line:
    #         line = line.replace('(','')
    #         line = line.replace(')','')
    #         line = line.replace('{','')
    #         line = line.replace('}','')
    #     elif 'ATOMIC_POSITIONS' in line:
    #         line = line.replace('(','')
    #         line = line.replace(')','')
    #         line = line.replace('{','')
    #         line = line.replace('}','')
    #     string_to_read += line
    # qe_input = PWInput.from_string(string_to_read)
    # struct = qe_input.structure
else:
    input_format=input_extension
    struct = Structure.from_file(input_filename)
    #struct=Structure.from_file(input_filename)

if output_extension not in list_not_QE:
    output_format='espresso-in'
    
    # QE_input: need to prepare Species card
    list_elements=[]
    for i in struct.species:
        if str(i) not in list_elements:
            list_elements.append(str(i))
    dict_pseudo={}
    for element in list_elements:
        dict_pseudo[element] = element+'.UPF'
    qe_output = PWInput(struct, pseudo=dict_pseudo, kpoints_mode='gamma')
    qe_output.write_file(output_filename)
    
elif output_extension == 'vasp':
    struct.to(fmt='poscar',filename=output_filename)
else:
    output_format=output_extension
    struct.to(fmt=output_extension, filename=output_filename)

#from ase import spacegroup
#from ase import spacegroup
#ase_structure=io.read(input_filename,format=input_format)
#sg_info = spacegroup.get_spacegroup(ase_structure)  #, symprec=1e-5
print('Space group: ',struct.get_space_group_info()[0], '(SPG# {0})'.format(struct.get_space_group_info()[1]))
#print('SPG number: ',struct.get_space_group_info()[1])

if flag_delete_file:
    os.remove('struct_convert_temporary.vasp')

#ase_structure=io.read(input_filename,format=input_format)
#io.write(output_filename, ase_structure, format=output_format)

