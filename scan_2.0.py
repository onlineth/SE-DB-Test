from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import numpy as np
import timeit
#
# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

plot_trks = True

iev_start = input("  Enter the even number to start (starting from 0) \n")
print '   Start at event number ', iev_start

# infile = open("randomized_files.list","r")
# nlist_all = pickle.load(infile)

# classified_files = open("classified_E_v2.0.list","a")
# nlist = nlist_all[iev_start:-1]

evt = 0

# for file in nlist:

file = 'single_electron/mctruehits_trk_4.dat'
print '   Scanning event number   ', evt + iev_start
print file
start_time = timeit.default_timer()
# -------------------------------------------------------------------------
# Read in the voxelized and MC tracks
# -------------------------------------------------------------------------
#     vtrk_file = "{0}/voxels_trk_{1}.dat".format(dat_base,evt)
#     mctrk_file = "{0}/mctruehits_trk_{1}.dat".format(dat_base,evt)
#     vtrk_file = mctrk_file
vtrk_file = file
mctrk_file = file
# print "===>  Event   ",evt + iev_start
evt += 1
# If no file exists for this event, continue to the next.

# if(not os.path.isfile(vtrk_file) or not os.path.isfile(mctrk_file)):
# print vtrk_file
# print "File not found"
# continue

# Read the voxelized track.
trktbl = np.loadtxt(vtrk_file)
vtrk_ID_temp = trktbl[:, 0]
vtrk_x = trktbl[:, 1]
vtrk_y = trktbl[:, 2]
vtrk_z = trktbl[:, 3]
vtrk_E = trktbl[:, 4]
print "Found {0} voxels".format(len(vtrk_ID_temp))

# Convert to integer IDs.
vtrk_ID = []
vtrk_neighb = []
for vid in vtrk_ID_temp:
    vtrk_ID.append(int(vid))
    vtrk_neighb.append([-1])
    # do not know how to create an empty list, insert "someting"

# Read the MC track.
mctrktbl = np.loadtxt(mctrk_file)
mctrk_ID_temp = mctrktbl[:, 0]
mctrk_x = mctrktbl[:, 1]
mctrk_y = mctrktbl[:, 2]
mctrk_z = mctrktbl[:, 3]
mctrk_E = mctrktbl[:, 4]
# if(debug > 0): print "Found {0} voxels".format(len(mctrk_ID_temp))

# Convert to integer IDs.
mctrk_ID = []
for mid in mctrk_ID_temp:
    mctrk_ID.append(int(mid))

if (plot_trks):

    fig = plt.figure(figsize=(20, 10))

    ax3 = fig.add_subplot(111, projection='3d')
    mctrk_col = []
    for energy in mctrk_E:
        mctrk_col.append(1000 * energy)

    psize = 5000 * mctrk_E
    s3 = ax3.scatter(mctrk_x, mctrk_y, mctrk_z, s=psize)
    #         for x,y,z,E in zip(mctrk_x,mctrk_y,mctrk_z,mctrk_E):
    #             s3 = ax3.plot(mctrk_x,mctrk_y,mctrk_z,'s',
    #                       markersize=int(mctrk_E*5000))
    # s3.set_edgecolors = s3.set_facecolors = lambda *args:None
    # this disables automatic setting of alpha relative of distance to camera

    #         colors = cm.rainbow(np.linspace(0, 1, len(mctrk_x)))
    #         ax3 = fig.add_subplot(111, projection='3d')
    #         for px,py,pz,c in zip(mctrk_x,mctrk_y,mctrk_z,colors):
    #             #ax3.plot(1.,1.,1.,'s')
    #             ax3.plot([px],[py],[pz],'.',color=c,markersize=4)
    #         ax3.plot([mctrk_x[0]],[mctrk_y[0]],[mctrk_z[0]],'o',color='blue',markersize=5)
    #         ax3.plot([mctrk_x[-1]],[mctrk_y[-1]],[mctrk_z[-1]],'s',color='blue',markersize=5)
    ax3.set_xlabel("x (mm)")
    ax3.set_ylabel("y (mm)")
    ax3.set_zlabel("z (mm)")

    lb_x = ax3.get_xticklabels()
    lb_y = ax3.get_yticklabels()
    lb_z = ax3.get_zticklabels()
    for lb in (lb_x + lb_y + lb_z):
        lb.set_fontsize(8)

    plt.show()

    classif = input("  classify 0(single el) - 10(double el)\n")
    print classif
    cl = "   {0} \n".format(classif)
    fout = file + cl
    classified_files.write(fout)
