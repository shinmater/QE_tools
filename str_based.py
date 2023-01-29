# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 10:47:48 2022

@author: yongjin
"""

import sys
import numpy as np

if len(sys.argv) ==1:
    sys.argv=['test','output.relax','input.relax', 'input_test.scf']

##############################################################################
########## Read POSCAR file and indexing each line with atom label
##############################################################################
if len(sys.argv) == 1:
    print('POSCAR is not provided')
    sys.exit()

## List of structures
# relaxation file can have multiple intermediate structures
list_structures = []
"""
list_structures - list:
    list of dict 'structure'
structure - dict, size of 2
    key 'CELL' -> list of 4 strings. CELL_PARAMETER information
    key 'SITES' ->  list, size of 'natom'+1
            information of atomic sites
"""  

relax_output=open(sys.argv[1],'r')
lines=relax_output.readlines()

parse_count = 0
for i,line in enumerate(lines):
    
    ## Number of atom is parsed from output file
    if 'number of atoms' in line:
        natom = int(line.split('=')[1])
    
    ## This is the indication of relaxation
#    elif 'Begin final' in line or 'End final' in line:
        
    ## This is the start of Cell parameters
    # it seems that this does not depend on ibrav = 0
    # Can vary based on (angstrom) or (alat)
    elif 'CELL_PARAMETERS' in line:
        if len(list_structures) == 0:
            list_structures.append({})
            list_structures[-1]['CELL'] = lines[i:i+4]
        elif 'CELL' in list_structures[-1].keys():
            list_structures.append({})
            list_structures[-1]['CELL'] = lines[i:i+4]
        else:
            list_structures[-1]['CELL'] = lines[i:i+4]
        #parse_count = natom + 6
        # this '+6' includes one blank line, and cell parameters, etc.
    
    elif 'ATOMIC_POSITIONS' in line:
        if len(list_structures) == 0:
            list_structures.append({})
            list_structures[-1]['SITES'] = lines[i:i+natom+1]
        elif 'SITES' in list_structures[-1].keys():
            list_structures.append({})
            list_structures[-1]['SITES'] = lines[i:i+natom+1]
        else:
            list_structures[-1]['SITES'] = lines[i:i+natom+1]
    
    # if parse_count != 0:
    #     list_structures[-1].append(line)
    #     parse_count -= 1
        
        

relax_input=open(sys.argv[2],'r')

if len(sys.argv) >= 4:
    scf_input_name = sys.argv[3]
else:
    scf_input_name = 'input.scf'
scf_input = open(scf_input_name,'w')

lines = relax_input.readlines()

# Initialize namelist
namelist = None
pass_count = 0

for line in lines:

    if pass_count != 0:
        pass_count -= 1
    
    elif '&' in line:
        #print(line.split('&'))
        namelist = line.split('&')[-1].strip()
        scf_input.write(line)
        
    elif 'calculation' in line and namelist.lower() == 'control':
        # print(line)
        index=line.find('calculation')
        value_start_idx = index + 11 + line[index+11:].find("'")
        value_end_idx = 2 + value_start_idx + line[value_start_idx+1:].find("'")
        
        new_line = line[:value_start_idx] + \
            "'scf'" + line[value_end_idx:]
        
        scf_input.write(new_line)
        
    elif 'occupations' in line and namelist.lower() == 'system':
        
        
        index=line.find('occupations')
        value_start_idx = index + 11 + line[index+11:].find("'")
        value_end_idx = 2 + value_start_idx + line[value_start_idx+1:].find("'")
        
        new_line = line[:value_start_idx] + \
            "'tetrahedra' !" + line[value_end_idx:]
        
        scf_input.write(new_line)
    
    elif '/' in line:
        namelist = None
        scf_input.write(line)
    elif 'CELL_PARAMETERS' in line:
        for print_line in list_structures[-1]['CELL']:
            scf_input.write(print_line)
        scf_input.write('\n')
        pass_count = 4
        
    elif 'ATOMIC_POSITIONS' in line:
        for print_line in list_structures[-1]['SITES']:
            scf_input.write(print_line)
        pass_count = natom + 1
        scf_input.write('\n')
        
    else:
        scf_input.write(line)

scf_input.close()