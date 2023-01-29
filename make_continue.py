# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 10:47:48 2022

@author: yongjin
To be updated:
1. support 'relax'-setting
"""

import sys
import re
#import numpy as np

# if len(sys.argv) ==1:
#     sys.argv=['test','output.relax','input.scf', 'input_test.scf']

##############################################################################
########## Read POSCAR file and indexing each line with atom label
##############################################################################
if len(sys.argv) == 1:
    print('POSCAR is not provided')
    sys.exit()

## List of structures
# relaxation file can have multiple intermediate structures
list_structures = []
list_cells = []
list_atomic_sites = []
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
    if 'nat=' in line.replace(" ",""):
        temp = line.replace(" ","")
        split_line = re.split('[\n,=]',temp)
        natom = int(split_line[split_line.index('nat')+1])   
    ## This is the indication of relaxation
#    elif 'Begin final' in line or 'End final' in line:
        
    ## This is the start of Cell parameters
    # it seems that this does not depend on ibrav = 0
    # Can vary based on (angstrom) or (alat)
    elif 'CELL_PARAMETERS' in line:
#        if len(list_structures) == 0:
            #list_structures.append({})
            #list_structures[-1]['CELL'] = lines[i:i+4]
        list_cells.append(lines[i:i+4])
#        elif 'CELL' in list_structures[-1].keys():
#            list_structures.append({})
#            list_structures[-1]['CELL'] = lines[i:i+4]
#        else:
#            list_structures[-1]['CELL'] = lines[i:i+4]
        #parse_count = natom + 6
        # this '+6' includes one blank line, and cell parameters, etc.
    
    elif 'ATOMIC_POSITIONS' in line:
        list_atomic_sites.append(lines[i:i+natom+1])
        # if len(list_structures) == 0:
        #     list_structures.append({})
        #     list_structures[-1]['SITES'] = lines[i:i+natom+1]
        # elif 'SITES' in list_structures[-1].keys():
        #     list_structures.append({})
        #     list_structures[-1]['SITES'] = lines[i:i+natom+1]
        # else:
        #     list_structures[-1]['SITES'] = lines[i:i+natom+1]
    
    # if parse_count != 0:
    #     list_structures[-1].append(line)
    #     parse_count -= 1
        

if len(list_cells) != len(list_atomic_sites):
    print("Warning: 'CELL_PARAMETERS' and 'ATOMIC_POSITIONS' are with different occurances")
        
#################################
##### Write a new input  ########
#################################

relax_input=open(sys.argv[2],'r')

if len(sys.argv) >= 4:
    scf_input_name = sys.argv[3]
else:
    scf_input_name = 'input.relax1'
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
        
    # elif 'calculation' in line and namelist.lower() == 'control':
    #     # print(line)
    #     index=line.find('calculation')
    #     value_start_idx = index + 11 + line[index+11:].find("'")
    #     value_end_idx = 2 + value_start_idx + line[value_start_idx+1:].find("'")
        
    #     new_line = line[:value_start_idx] + \
    #         "'scf'" + line[value_end_idx:]
        
    #     scf_input.write(new_line)
        
    # elif 'occupations' in line and namelist.lower() == 'system':
        
        
    #     index=line.find('occupations')
    #     value_start_idx = index + 11 + line[index+11:].find("'")
    #     value_end_idx = 2 + value_start_idx + line[value_start_idx+1:].find("'")
        
    #     new_line = line[:value_start_idx] + \
    #         "'tetrahedra' !" + line[value_end_idx:]
        
    #     scf_input.write(new_line)

    # elif 'degauss' in line and namelist.lower() == 'system':
        
    #     index=line.find('degauss')
    #     value_start_idx = index + 7 + line[index+7:].find("=")
        
    #     value_end_idx = 3 + value_start_idx + line[value_start_idx+1:].find("\n")
        
    #     new_line = line[:value_start_idx] + \
    #         "=0.001"
    #     scf_input.write(new_line)
    #     scf_input.write('\n')

    elif '/' in line:
        namelist = None
        scf_input.write(line)
    elif 'CELL_PARAMETERS' in line and len(list_cells) != 0:
#        for print_line in list_structures[-1]['CELL']:
#            scf_input.write(print_line)
#        scf_input.write('\n')
        for cell_line in list_cells[-1]:
            scf_input.write(cell_line)
        scf_input.write('\n')
        pass_count = 4
        
    elif 'ATOMIC_POSITIONS' in line:
#        for print_line in list_structures[-1]['SITES']:
#            scf_input.write(print_line)
        for site_line in list_atomic_sites[-1]:
            scf_input.write(site_line)
        pass_count = natom + 1
        scf_input.write('\n')
#    elif '  4 1 4 0 0 0' in line:
#        scf_input.write('  8 3 8 0 0 0\n')
    elif 'ecutwfc = 50' in line:
        scf_input.write('    ecutwfc = 75 !, ecutrho =720, !for PAW ecutrho=4*ecutwfc, but need test\n')
#    elif '  5 2 5 0 0 0' in line:
#        scf_input.write('  8 3 8 0 0 0\n')
    elif 'ecutwfc = 60' in line:
        scf_input.write('    ecutwfc = 75 !, ecutrho =720, !for PAW ecutrho=4*ecutwfc, but need test\n')

        
    else:
        scf_input.write(line)

scf_input.close()