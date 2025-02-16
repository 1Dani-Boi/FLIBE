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

device = anp.generate_device("U", 20)

# Plotting
plot = openmc.Plot()
plot.filename = 'geometry_plot'
plot.basis = 'xz'
plot.origin = (350, 0, 0)
plot.width = (700, 800)
plot.pixels = (plot.width[0]*10, plot.width[1]*10)
plot.color_by = 'cell'

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
r_grid = np.linspace(0, 600, num=50) #[NEW] original: (25, 200, num=25)
z_grid = np.linspace(-700, 700, num=100) #[NEW] original: (-200, 200, num=50)
mesh = openmc.CylindricalMesh(r_grid=r_grid, z_grid=z_grid) #[NEW]
mesh.phi_grid = np.array([0, (2 * np.pi)/(18 * 2)])
mesh_filter = openmc.MeshFilter(mesh)

device.add_tally('Mesh Tally', ['flux', '(n,Xt)', 'heating-local', 'absorption'], filters=[mesh_filter])

# """ FLiBe Tally """
flibe_filter = openmc.MaterialFilter(device.doped_flibe_blanket) #device.doped_flibe, initially wanted 'doped_mat' which doesn't exist

device.add_tally('FLiBe Tally', ['(n,Xt)', 'fission', 'kappa-fission', 'fission-q-prompt', 'fission-q-recoverable', 'heating', 'heating-local'], filters=[flibe_filter])

# ==============================================================================
# Run
# ==============================================================================

device.settings.photon_transport = True

device.build()

device.export_to_xml(remove_surfs=True)

#openmc.plot_geometry()

'''NEW'''
# Set the number of particles to run
device.settings.particles = int(1e4)  # 1e3 = 1000 particles
# Optionally, set other simulation parameters (e.g., number of batches, inactive batches, etc.)
device.settings.batches = 10  # Number of batches (for example)
device.settings.inactive = 2  # Number of inactive batches
#remove old output files
for file in os.listdir('.'):
    if file.endswith('.h5'):
        os.remove(file)
# Run the simulation
device.run()

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
out_file = ""
for file in os.listdir('.'):
    if file.endswith('.h5'):
        if file != "summary.h5":
            out_file = file
command = ["openmc-plot-mesh-tally", out_file]

# Run the command
subprocess.run(command)