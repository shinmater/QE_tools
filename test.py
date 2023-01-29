from pymatgen.io.pwscf import PWInput
#from pymatgen.io.qbox import QboxInput
from pymatgen.io.vasp import Poscar
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.symmetry.bandstructure import HighSymmKpath
 
# read bulk MgO input file
qe_bulk = PWInput.from_file('bulk.in')
# print structure
print(qe_bulk.structure)

# The bulk calculation is performed with the conventional (cubic) unitcell.
# Let's analyze the symmetry of the structure and see whether we can reduce it.
analyzer = SpacegroupAnalyzer(qe_bulk.structure)
# we check the symmetry and space-group number
print('Space Group Symbol: ', analyzer.get_space_group_symbol())
print('Space Group Number: ', analyzer.get_space_group_number())
 
#We can reduce the unitcell-size using symmetry:
primitive = analyzer.get_primitive_standard_structure()
print(primitive)
 
# Let's generate a QE input file for the reduced unitcell
# First we define the pseudopotential files in a dictionary.
pseudo = {
    "Mg": "Mg_ONCV_PBE-1.2.upf",
    "O" : "O_ONCV_PBE-1.2.upf"
}
# Now we create the input using the structure and pseudopotential dict.
qe_primitive = PWInput(primitive, pseudo=pseudo, kpoints_mode='gamma')
# And we write it to file
qe_primitive.write_file('primitive.in')
 
# We create a 2x2x2 supercell of the primitive unitcell
primitive222 = (2,2,2) * primitive
 
# Write supercell to file
qe_supercell = PWInput(primitive222, pseudo=pseudo, kpoints_mode='gamma')
qe_supercell.write_file('supercell.in')
 
# generate kpath object for symmetry-reduced structure
kpath = HighSymmKpath(primitive)
#write high-symmetry points
print(kpath.kpath)
 
 
# We generate a list of symmetry points and their position in reciprocal space
kpoints=[]
for i in range(len(kpath.kpath['path'][0])):
    kpoints.append(kpath.kpath['kpoints'][kpath.kpath['path'][0][i]])
 
 
# Now we create a QE input file with these high-symmetry points and write it to file
pw_bandstr = PWInput(primitive,
                     pseudo=pseudo,
                     kpoints_mode="crystal_b",
                     kpoints_grid=kpoints)
pw_bandstr.write_file('bandstructure.in')
 
# Let's define pseudopotential files for qbox
pseudo_qbox = {
    "Mg": "Mg_ONCV_PBE-1.2.xml",
    "O" : "O_ONCV_PBE-1.2.xml"
}
# Generate Qbox Input Object and write it to file
# qbox = QboxInput(primitive, pseudos=pseudo)
# qbox.write_file('primitive.i')
 
# vasp_bn = Poscar.from_file('bn.poscar')
 
# pseudos = {'B':'B_ONCV_PBE-1.2.upf',
#            'N':'N_ONCV_PBE-1.2.upf'}
# PWInput(vasp_bn.structure, pseudo= pseudos, kpoints_mode='gamma').write_file('bn.in')