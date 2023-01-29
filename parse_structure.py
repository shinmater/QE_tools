# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 10:47:48 2022

@author: yongjin
"""

import sys
from ase import io
import numpy as np

if len(sys.argv) ==1:
    sys.argv=['test','output.relax','structure.vasp', 'input_test.scf']

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
        
structure=list_structures[-1]

list_labels = [item.split()[0] for item in structure['SITES'][1:]]
list_label_reduced = []
for item in list_labels:
    if item not in list_label_reduced:
        list_label_reduced.append(item)

ntype=len(set(list_labels))

### required field
list_text=[
    '&CONTROL\n',
    "  calculation = 'scf',\n",
    "/\n",
    '&SYSTEM\n',
    "  ibrav = 0,\n",
    "  nat = {0},\n".format(natom),
    "  ntype = {0},\n".format(ntype),
    "/\n",
    '&ELECTRONS\n',
    "/\n",
    '&IONS\n',
    "/\n",
    '&CELL\n',
    "/\n"
    ]
### atomic species
list_text.append("ATOMIC_SPECIES\n")
for item in list_label_reduced:
    list_text.append("{0} 1.00 None\n".format(item))

list_text.append('\n')
list_text.append("K_POINTS gamma\n")
list_text.append('\n')

### WRITE down to Espresso-in format first

pw_file=open('temp.in','w')
for line in list_text:
    pw_file.write(line)
for line in structure['CELL']:
    pw_file.write(line)
pw_file.write('\n')
for line in structure['SITES']:
    pw_file.write(line)
pw_file.close()


if len(sys.argv) >= 3:
    vasp_poscar_name = sys.argv[2]
else:
    vasp_poscar_name = 'structure.vasp'

poscar_file = open(vasp_poscar_name,'w')


### PRINT FINAL STRUCTURE ###

last_struct=list_structures[-1]

#poscar_file=open(filename,'w')
poscar_file.write("Generated POSCAR file\n") #first comment line
poscar_file.write("1.0\n") # scale 
# Print lattice part
#for i in range(np.shape(lattice)[0]):
#    poscar_file.write("{0:20.10f} {1:20.10f} {2:20.10f}\n".format(lattice[i,0],lattice[i,1],lattice[i,2]))
for line in last_struct['CELL'][1:]:
    poscar_file.write(line)


### Need to organize the type of elements and number of atoms
# list_elements is to print in order.
# Dictionary could print in undesired order


# function
def parse_element(string):
    """
    print element name
    This is for reduce label. for example from Co3 to Co.
    input: string 
    ex) Co, Co3, Fe3, etc.
    output: element_name
    ex) Co, Co, Fe, etc.
    """
    # LIST OF ELEMENTS
    elements = ['H','He','Li','Be','B','C','N','O','F','Ne',
                'Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca',
                'Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn',
                'Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr',
                'Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn',
                'Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd',
                'Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb',
                'Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg',
                'Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th',
                'Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm',
                'Md','No','Lr','Rf','Db','Sg','Bh','Hs','Mt','Ds',
                'Rg','Cn','Nh','Fl','Mc','Lv','Ts','Og']
    if string in elements:
        element_name=string
    else:
        element_name=string[:2]
    return element_name

line = last_struct['SITES'][1]
label,xcoord_str,ycoord_str,zcoord_str = line.split()
specie = parse_element(label)

list_elements = [specie]
list_num_elements = [1]

# starts from the second line
for i,line in enumerate(last_struct['SITES'][2:]):
    # example of line:
    # Sr       5.501155306   1.753542039   2.708184595
    #print(line.split()[0])
    label,xcoord_str,ycoord_str,zcoord_str = line.split()
    specie = parse_element(label)
    if specie == list_elements[-1]:
        list_num_elements[-1] +=1
    else:
        list_elements.append(specie)
        list_num_elements.append(1)

    
### Print elements
poscar_file.write("  "+"  ".join('%3s' % entry for entry in list_elements))
poscar_file.write("\n")

### Print the number of atoms for each element
poscar_file.write("  "+"  ".join('%3d' % entry for entry in list_num_elements))
poscar_file.write("\n")

### direct or cartesian
# 
if 'angstrom' in last_struct['SITES'][0].split()[-1]:
    poscar_file.write("Carteisan\n")
else: # crystal
    poscar_file.write("Direct\n")

for i,line in enumerate(last_struct['SITES'][1:]):
    # example of line:
    # Sr       5.501155306   1.753542039   2.708184595
    #print(line.split()[0])
    label,xcoord_str,ycoord_str,zcoord_str = line.split()
    poscar_file.write("  "+"      ".join('%12s' % entry for entry in [xcoord_str,ycoord_str,zcoord_str]))
    poscar_file.write('  ! atm#{0:-3d}  '.format(i+1)+label+'\n')


poscar_file.close()


### Make dictionary 


#ase_structure=io.read('temp.in',format="espresso-in")
#io.write(vasp_poscar_name, ase_structure, format='vasp')

