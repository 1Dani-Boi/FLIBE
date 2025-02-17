import arc_nonproliferation as anp
import openmc
import numpy as np
import os
import sys
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import subprocess

# ==============================================================================
# Geometry
# ==============================================================================

device = anp.generate_device("U", 0)

# Plotting
plot = openmc.Plot()
plot.filename = 'geometry_plot'
plot.basis = 'xz'
plot.origin = (350, 0, 0)
plot.width = (700, 800)
plot.pixels = (plot.width[0]*10, plot.width[1]*10)
color_me = ['gray' , 'blue', 'yellow', 'orange','olive','purple','cyan','white']
color = {device._cells[0]: color_me[0], device._cells[1]: color_me[1], device._cells[2]: color_me[2], device._cells[3]: color_me[3],
        device._cells[4]: color_me[4], device._cells[5]: color_me[5], device._cells[6]: color_me[6], device._cells[7]: color_me[7]}
plot.colors = color

for count, cell in enumerate(device._cells):
    print(f'Device name: {cell.name} with color: {color_me[count]}')

# for key, value in color:
#     print(f'device name: {key.name} with color: {value}')
# print(device._cells)
# print('======================, device._cells[0]: 'r')
# print(device._cells[1].name)
# print('======================================================')
plot.highlight_domains(geometry=device.geometry, domains=device._cells)

plots = openmc.Plots([plot])
plots.export_to_xml()


# ==============================================================================
# Settings
# ==============================================================================

""" Source Definition """
source = openmc.Source()
source.space = openmc.stats.CylindricalIndependent(openmc.stats.Discrete(450, 1), openmc.stats.Uniform(a=-np.pi/18, b=np.pi/18), openmc.stats.Discrete(0, 1))
source.angles = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14.1E6], [1.0])

device.settings.source = source

# ==============================================================================
# Tallies
# ==============================================================================
# """ Cylindrical Mesh Tally """
r_grid = np.linspace(0, 600, num=50) #[NEW] original: (25, 200, num=25), 0, 600
z_grid = np.linspace(-700, 700, num=100) #[NEW] original: (-200, 200, num=50), -700, 700
mesh = openmc.CylindricalMesh(r_grid=r_grid, z_grid=z_grid) #[NEW]
mesh.phi_grid = np.array([0, (2 * np.pi)/(18 * 2)])
mesh_filter = openmc.MeshFilter(mesh)

device.add_tally('Mesh Tally', ['flux', '(n,Xt)', 'heating-local', 'absorption'], filters=[mesh_filter])

# """ FLiBe Tally """
flibe_filter = openmc.MaterialFilter(device.doped_flibe_blanket) #device.doped_flibe, initially wanted 'doped_mat' which doesn't exist

device.add_tally('FLiBe Tally', ['(n,Xt)', 'fission', 'kappa-fission', 'fission-q-prompt', 'fission-q-recoverable', 'heating', 'heating-local'], filters=[flibe_filter])

flibe_filter2 = openmc.MaterialFilter(device.doped_flibe_channels) #device.doped_flibe, initially wanted 'doped_mat' which doesn't exist

device.add_tally('FLiBe Tally', ['(n,Xt)', 'fission', 'kappa-fission', 'fission-q-prompt', 'fission-q-recoverable', 'heating', 'heating-local'], filters=[flibe_filter2])

# ==============================================================================
# Run
# ==============================================================================

device.settings.photon_transport = True

device.build()

device.export_to_xml(remove_surfs=True)

openmc.plot_geometry()

'''NEW'''
# Set the number of particles to run
device.settings.particles = int(1e2)  # 1e3 = 1000 particles
# Optionally, set other simulation parameters (e.g., number of batches, inactive batches, etc.)
device.settings.batches = 10  # Number of batches (for example)
device.settings.inactive = 2  # Number of inactive batches
#remove old output files
# for file in os.listdir('.'):
#     if file.endswith('.h5'):
#         os.remove(file)
# Run the simulation
# device.run()

try:
    if sys.argv[1] is not None:
        os.mkdir(str(sys.argv[1]))
        device.move_files(str(sys.argv[1]))
        print("OpenMC files moved to new directory:", str(sys.argv[1]))

except:
    print("No directory specified, using this one")

'''NEW
not currently working'''
# =============================================
# tally plot
# =============================================
# out_file = ""
# for file in os.listdir('.'):
#     if file.endswith('.h5'):
#         if file != "summary.h5":
#             out_file = file
# command = ["openmc-plot-mesh-tally", out_file]

# # Run the command
# subprocess.run(command)