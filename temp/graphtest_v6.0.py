"""

graphtest.py

Tests graph algorithms for voxelized tracks

Notes:
 - the networkx package does not preserve the node ordering; nodes in unordered
   graphs are expected to be such that the order doesn't matter
 - there could be multiple MSTs, and this is likely when using voxels
   because the distances are discrete (temporary fix, add some negligible
   distance varying based on voxel ID number); also in MST traversal begin
   with a node that has only 1 neighbor - as there are likely to be multiple,
   begin with the one that has lowest voxel ID
   
   * results do vary based on how the tree is traversed and where the starting
     node is

    current problems: (07/23/2015)  90,94,116,126,148
@author: josh
"""


#from mpl_toolkits.mplot3d import Axes3D
from axes3d import Axes3D
from math import *
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cm as cm
import random as rd
import numpy as np
import scipy.integrate as itg
import networkx as nx
import os
import sys

# Options
evt_start = 10;
evt_end = 91;
print_trks = False;
plot_trks = True;

voxelsize = 2;
evt_type = "single_electron";
out_fmt = "png";
#dat_base = "/Users/jrenner/googledrive/BEXT/recpack_test_data";
dat_base = "/download/para/NEXT/TPC/single_electron_evts/{0}".format(evt_type);
plt_base = "/download/para/NEXT/TPC/mst";
debug = 0;
npavg = 10;
endpt_dist = 10;   # distance between track endpoints that merit identification of a node
node_dist = 5;     # minimum distance between nodes
min_path_voxels = 0.0;
path_overlap_tol = 0;
dist_cut = 5.      # maximal distance of points to be included in the tree

node_dist_sq = node_dist**2;
endpt_dist_sq = endpt_dist**2;


















# Returns the longest path for a directed graph.
# From: http://stackoverflow.com/questions/17985202/networkx-efficiently-find-absolute-longest-path-in-digraph
def longest_path(G):
    dist = {} # stores [node, distance] pair
    for node in nx.topological_sort(G):
        # pairs of dist,node for all incoming edges
        pairs = [(dist[v][0]+1,v) for v in G.pred[node]] 
        if pairs:
            dist[node] = max(pairs)
        else:
            dist[node] = (0, node)
    node,(length,_)  = max(dist.items(), key=lambda x:x[1])
    path = []
    while length > 0:
        path.append(node)
        length,node = dist[node]
    return list(reversed(path))
    
# Calculates and returns the direction vector from point 1 to point 2.
def dir_vec(x1,y1,z1,x2,y2,z2):
    vd = np.array([(x2-x1),(y2-y1),(z2-z1)]);
    vlen = sqrt(vd[0]**2 + vd[1]**2 + vd[2]**2);
    vd = vd/vlen;
    return vd;
    
# TrackNode class
#  Node types:
#   0: normal
#   1: end node
#   2: vertex/branch point
#   3: end node that should be connected to another part of the track
#       (node specified as "link")
class TrackNode:    
    
    # Creates a new TrackNode
    def __init__(self,idnum):
        self.id = idnum;
        self.visited = False;
        self.type = 0;
        self.link = -1;  # node to which this is connected for type 3
        
    def __repr__(self):
        return "Node {0}, type {1}, visited {2}".format(self.id,self.type,self.visited);

    def __str__(self):
        return "Node {0}, type {1}, visited {2}".format(self.id,self.type,self.visited);
        
# TrackSegment class
class TrackSegment:
        
    # Creates a new TrackSegment with specified start and end nodes.
    def __init__(self,inode,fnode):
        self.inode = inode;
        self.fnode = fnode;
        self.path = [];
        self.length = 0.0;
        
    def set_path(self,pth):
        self.path = pth;
        self.inode = pth[0];
        self.fnode = pth[-1];
    
    def set_len(self,length):
        self.length = length;
   
    def __repr__(self):
        return "Segment: node {0} (type {1}) to node {2} (type {3})\n".format(self.inode.id,self.inode.type,self.fnode.id,self.fnode.type); 
     
    def __str__(self):
        return "Segment: node {0} (type {1}) to node {2} (type {3})".format(self.inode.id,self.inode.type,self.fnode.id,self.fnode.type);

# ---------------------------------------------------------------------------
# Extreme-finding methods
# ---------------------------------------------------------------------------

# Finds the extremes as:
#  - extreme 1 is the blob with more than Nmin voxels and greatest Eblob/Nvoxels
#  - extreme 2 is the voxel to which the shortest path from the first extreme
#    to that voxel is the longest of all other voxels
#  - extreme 1 will correspond to the end of the track and extreme 2 to the beginning
#
# gtrk: the track graph
# rblob: the blob radius to be used in the analysis
# Nmin: the minimum number of voxels to be considered a blob
# trk_ID: the list of voxel ID numbers
# trk_x: the list of voxel x-values
# trk_y: the list of voxel y-values
# trk_z: the list of voxel z-values
# trk_E: the list of voxel energy values
def find_extremes_EoverN(gtrk,rblob,Nmin,trk_ID,trk_x,trk_y,trk_z,trk_E):
    
    # Iterate through all voxels to find the maximum energy blob.
    eovern_max = -1; vblob_max = -1
    for vID1,vx1,vy1,vz1,vE1 in zip(trk_ID,trk_x,trk_y,trk_z,trk_E):
    
        # For this voxel, calculate the blob energy.
        eblob = 0.; Nvox = 0;
        for vID2,vx2,vy2,vz2,vE2 in zip(trk_ID,trk_x,trk_y,trk_z,trk_E):
            if(sqrt((vx2-vx1)**2 + (vy2-vy1)**2 + (vz2-vz1)**2) < rblob):
                  eblob += vE2;
                  Nvox += 1;
        
        eblob /= Nvox;
        if(eblob > eovern_max and Nvox > Nmin):
            eovern_max = eblob;
            vblob_max = vID1;

    # Iterate through all voxels to find the one with the longest shortest path
    #  from the center of the maximum blob.
    max_short = -1; vlong_short = -1;
    for vID1,vx1,vy1,vz1,vE1 in zip(trk_ID,trk_x,trk_y,trk_z,trk_E):
        #pth = nx.astar_path(trk,vblob_max,vID1);
        pth = nx.shortest_path(gtrk,vblob_max,vID1,"weight");
        plen = len(pth);
        if(plen > max_short):
            max_short = plen;
            vlong_short = vID1;
    
    if(debug > 0):
        print "Found blob at voxel {0}, beginning of track at voxel {1}".format(vblob_max,vlong_short);
        
    return vlong_short,vblob_max;

# Find the extremes as the two voxels with the longest shortest path
#  between them.
#
# gtrk: the track graph    
def find_extremes_Paolina(gtrk):
    
    # Iterate through all nodes, and calculate the shortest path from that node to each other node.
    max_sdist = -1; n1f = -1; n2f = -1;
    for n1 in gtrk:
        for n2 in gtrk:
            pth = nx.shortest_path(gtrk,n1,n2,"weight");
            plen = len(pth);
            if(plen > max_sdist):
                max_sdist = plen;
                n1f = n1; n2f = n2;
    
    return n1f,n2f;
    
# Finds the segments using a minimum spanning tree.
def find_segments_mst(mst,adjMat,xpos,ypos,zpos,nodesMarked=False):
    
    # Get the nodes of the MST.
    mst_nodes = nx.nodes(mst); #nx.topological_sort(mst);
    
    # Find a node with only one neighbor in the tree to use as the starting point.
    # If several are found, by default use the one with the lowest ID.
    snodes = [];
    for nd in mst_nodes:
        nn = mst.neighbors(nd);
        if(len(nn) == 1):
            snodes.append(nd);
    if(len(snodes) == 0):
        snode = mst_nodes[0];
    else:
        if(debug >= 0): print "Found {0} starting nodes.".format(len(snodes));
        snode = snodes[0];
        for sn in snodes:
            if(sn.id > snode.id):
                snode = sn;
    if(debug > 1): print "Set to starting node {0}".format(snode.id);
    snode.type = 1;
        
    if(debug >= 0): print "Found node {0} with 1 neighbor.".format(snode);
        
    # Traverse the MST, finding all segments in the tree.
    segments = []; currpth = [];
    (fnode, dist) = traverse_mst(mst,adjMat,snode,-1,segments,currpth);

    # Create the initial track segment.
    nseg = TrackSegment(currpth[0],currpth[-1]);
    nseg.set_path(currpth);
    nseg.set_len(path_length(mst,adjMat,currpth));
    segments.append(nseg);

    return segments;
    
# Traverses the MST, adding segments to the list as they are found.
def traverse_mst(mst,adjMat,node,prev,segments,currpth):
    #print "traverse_mst  debug = ",debug
    if(debug > 0): print "[traverse_mst]: node = {0}, prev = {1}".format(node,prev);
    
    # Get all neighboring nodes.
    nnodes = mst.neighbors(node);
    
    # If multiple successors, this node is a type 2 node, and the proceeding segments must be obtained.
    if(len(nnodes) > 2):

        if(debug > 1): print "-- Multiple successors: len(nnodes=)" ,len(nnodes);
        node.type = 2;

        num_seg = 0;
        ls_fnode = -1; ls_dist = -1.0;  # save "last segment" variables
        for nbr in nnodes:
            if(nbr != prev):    
                
                # Traverse in the direction of this neighbor.
                currpth2 = [];
                (fnode, dist) = traverse_mst(mst,adjMat,nbr,node,segments,currpth2);
                currpth2.append(node);
                
                # For end segments longer than some given length and for inner segments, create a new segment.
                if(dist > min_path_voxels or fnode.type == 2):
                    nseg = TrackSegment(currpth2[0],currpth2[-1]);
                    nseg.set_path(currpth2);
                    nseg.set_len(path_length(mst,adjMat,currpth2));
                    segments.append(nseg);
                    ls_fnode = fnode; ls_dist = dist;
                    num_seg += 1;
                
        # If we have no segments, consider this an end node.
        if(num_seg == 0):
            if(debug > 1): print "-- Found end node";
            node.type = 1;
            currpth.append(node);
            return (node,0.0);
        # If we only have 1 segment, do not consider this a segment end.
        elif(num_seg == 1):
            if(debug > 1): print "-- Not enough subsegments; continuing as one continuous segment";
            
            # This segment should not go in the segment array separately, as it is part of the current segment.
            nseg = segments.pop();
            for pnode in nseg.path: currpth.append(pnode);
            #currpth.append(node);
            return (ls_fnode,ls_dist+1.0);
        
        # Otherwise, this is an inner node.
        if(debug > 1): print "-- Found inner node";
        currpth.append(node);
        return (node,0.0);

    # Exactly one successor.        
    elif(len(nnodes) == 2 or (len(nnodes) == 1 and prev == -1)):
        
        # Select the neighbor that is not the predecessor.
        nextnd = -1;
        for nbr in nnodes:
            if(nbr != prev):
                nextnd = nbr;
                break;
        if(debug > 1): print "-- Single successor, next neighbor {0}".format(nextnd);
        
        # Continue the traversal in the direction of this neighbor.
        (fnode,dist) = traverse_mst(mst,adjMat,nextnd,node,segments,currpth);
        currpth.append(node);
        return (fnode,dist+1.0);
        
    # Error: node is completely isolated.
    elif(len(nnodes) < 1):
        print "ERROR: node with no neighbors";
        
    # No successors (end of path).
    else:
        
        if(debug > 1): print "-- No successors; end of segment";
        
        # No connections unaccounted for.
        node.type = 1;
        currpth.append(node);
        return (node,0.0);
      
# Determines whether any node in path "pth" coincides with any nodes in the paths
#  of the segments in the specified list "segments," with the exception of the
#  two endpoints n1 and n2.
def is_overlapped(pth,n1,n2,segments):
    
    # Return True if the path only consists of 2 nodes (two endpoints), as this
    #  means that the segments are already joined.
    if(len(pth) < 2):
        return True;

    # Iterate through the segments and find any overlapping nodes.
    for seg in segments:
        noverlap = 0;
        for pnode in pth:
            for snode in seg.path:
                if(pnode == snode and pnode != n1 and pnode != n2):
                    noverlap += 1;
        if(noverlap > path_overlap_tol):
            return True;

    # No coincidence was found in any segment.
    return False;
      
# Attempts to find a path in the specified graph from the given node to the 
#  endpoints of all segments in the given segments array, ensuring that no 
#  nodes in the path coincide with any nodes of any segment except for the 
#  endpoint of the segments which it connects.
#
# If a path is found, that path is returned as a segment.
def match_to_segments(node,nseg,segments,gtrk):
    
    if(debug > 2): print "Attempting to find additional paths from node {0}".format(node);
    
    # Iterate through segments, determining if this node is already connected
    #  to a segment.
    for seg in segments:
        
        # Skip the same segment.
        if(seg == nseg): continue;
        
        # Get the endpoints.
        ep1 = seg.inode;
        ep2 = seg.fnode;
        
        if(node == ep1 or node == ep2):
            if(debug > 1): print "Already connected to either {0} or {1}".format(ep1,ep2);
            return 0;
    
    # Iterate through segments, attempting to match the node to an endpoint.
    for seg in segments:
        
        # Get the endpoints.
        ep1 = seg.inode;
        ep2 = seg.fnode;
        
        # Get the paths to the endpoints.
        pth1 = nx.shortest_path(gtrk,node,ep1);
        pth2 = nx.shortest_path(gtrk,node,ep2);

        # Ensure no overlap with any other nodes in any segments.
        ovr1 = is_overlapped(pth1,node,ep1,segments);
        ovr2 = is_overlapped(pth2,node,ep2,segments);
        
        # Return the path as a segment if one is found.
        if(not ovr1 and not ovr2):
            print "ERROR, found non-overlapping paths from both endpoints.";
            return 0;
        elif(not ovr1):
            if(debug > 2): print "Found additional path from {0} to {1}".format(pth1[0],pth1[-1]);
            seg1 = TrackSegment(pth1[0],pth1[-1]);
            seg1.set_path(pth1);
            return seg1;
        elif(not ovr2):
            if(debug > 2): print "Found additional path from {0} to {1}".format(pth2[0],pth2[-1]);
            seg2 = TrackSegment(pth2[0],pth2[-1]);
            seg2.set_path(pth2);
            return seg2;
        
    # Return 0 if no path is found.
    return 0;

# Computes the path length of the given list of nodes on the given graph.
def path_length(grph,adjMat,nodes):

    plen = 0.0;    
    edges = grph.edges(nodes);
    for ed in edges:
        #print ed[1];
        plen += adjMat[ed[0].id][ed[1].id];
        
    return plen;

# Connect two segments
def connect_segments(seg1,seg2):
    
    n1i = seg1.inode; n1f = seg1.fnode;
    n2i = seg2.inode; n2f = seg2.fnode;
    if(debug > 1): print "[connect_segments] seg1 from {0} to {1}, seg2 from {2} to {3}".format(n1i,n1f,n2i,n2f);

    # Find the uncommon nodes.
    if(n1i == n2i or n1i == n2f): ncommon = n1i;
    elif(n1f == n2i or n1f == n2f): ncommon = n1f;
    else:
        print "ERROR: attempting to connect two segments that do not share a common node!";
        return 0;

    # Find the uncommon nodes.    
    if(ncommon == n1f): n1 = n1i;
    else: n1 = n1f;
    if(ncommon == n2f): n2 = n2i;
    else: n2 = n2f;
        
    # Make the connecting segment n1 to n2.
    if(debug > 1): print "[connect_segments] creating segment connecting {0} to {1}".format(n1,n2);
    sconn = TrackSegment(n1,n2);
    pth1 = seg1.path;
    pth2 = seg2.path;
    if(debug > 1): print "-- Path 1 contains nodes from {0} to {1}; Path 2 contains nodes from {2} to {3}".format(pth1[0],pth1[-1],pth2[0],pth2[-1]);

    # Make sure we have the correct orientation for the individual segment paths.    
    if(n1 == pth1[-1]): pth1.reverse();
    elif(n1 != pth1[0]):
        print "ERROR: path for segment 1 ({0} to {1}) does not contain n1 = {2}".format(seg1.inode,seg1.fnode,n1);
        print pth1;
        return 0;
    if(n2 == pth2[0]): pth2.reverse();
    elif(n2 != pth2[-1]):
        print "ERROR: path for segment 2 ({0} to {1}) does not contain n2 = {2}".format(seg2.inode,seg2.fnode,n2);
        print pth2;
        return 0;
        
    # Make the connected path.
    cpath = [];
    for nn1 in pth1:
        cpath.append(nn1);
    for nn2 in pth2:
        cpath.append(nn2);

    # Assign the path to the segment.
    sconn.set_path(cpath);

    return sconn;
    
# Connect the list of segments.
def connect_segment_in_list(seg,segments):
    
    if(debug > 1): print "[connect_segment_in_list] Connecting segment {0}".format(seg);

    # Keep track of whether a connection was made.
    connection = False;
    
    # Final list of connected segments.
    segments_f = [];
    
    # Attempt to find connections and make them as they are found.
    scurr = seg;
    for ss in segments:
        
        # Ignore the same segment.
        if(ss == seg): continue;
        
        # Connect the segment to the current segment if an endpoint matches and there is no third segment with the
        #  same endpoint.
        make_connection = False;
        if(scurr.inode == ss.inode or scurr.inode == ss.fnode):
            make_connection = True;
            # Ensure there is no third segment connected at inode of scurr.
            for s2 in segments:
                if((s2.inode == scurr.inode or s2.fnode == scurr.inode) and s2 != scurr and s2 != ss):
                    make_connection = False;
        if(scurr.fnode == ss.inode or scurr.fnode == ss.fnode):
            make_connection = True;
            # Ensure there is no third segment connected at fnode of scurr.
            for s2 in segments:
                if((s2.inode == scurr.fnode or s2.fnode == scurr.fnode) and s2 != scurr and s2 != ss):
                    make_connection = False;
                    
        # Make the connection if this should be the case.
        if(make_connection):
            sconn = connect_segments(scurr,ss);
            scurr = sconn;
            if(debug > 2): print "-- Connection found with segment {0}".format(ss);
            connection = True;
        else:
            segments_f.append(ss);
            
    # Append the connected segment.
    segments_f.append(scurr);
    
    return (connection,segments_f);
    

# Connect the tree
def connect_tree(tree):
    
    connected = False;
    
    # Iterate through all nodes, combining the edges connecting two nodes
    #  through one node whose only neighbors are those two connected nodes.
    for nd in tree.nodes():
        
        # Get all edges of this node.
        edges = tree.edges(nd);
        
        # If exactly two edges to two different neighbors, the edges
        #  may be combined.
        if(len(edges) == 2):
            
            # Get the two edges.
            ed0 = edges[0];
            ed1 = edges[1];
            print "Got edge {0} and edge {1}".format(ed0,ed1);
            print "Edge 0 segment from {0} to {1}".format(tree[ed0[0]][ed0[1]]['slist'][0].inode,tree[ed0[0]][ed0[1]]['slist'][0].fnode);
            print "Edge 1 segment from {0} to {1}".format(tree[ed1[0]][ed1[1]]['slist'][0].inode,tree[ed1[0]][ed1[1]]['slist'][0].fnode);
            
            # Get the two neighbors.
            nb0 = ed0[0];
            if(nb0 == nd): nb0 = ed0[1];
            nb1 = ed1[0];
            if(nb1 == nd): nb1 = ed1[1];
            print "Found neighbors {0} and {1}".format(nb0,nb1);
            
            nseg0 = len(tree[ed0[0]][ed0[1]]['slist']);
            nseg1 = len(tree[ed1[0]][ed1[1]]['slist']);
                        
            # If the neighbors are not the same, proceed with the connection.
            if(nb0 != nb1 and nseg0 == 1 and nseg1 == 1):
                
                # Make the connection.
                sconn = connect_segments(tree[ed0[0]][ed0[1]]['slist'][0],tree[ed1[0]][ed1[1]]['slist'][0]);

                if(sconn != 0):

                    # Remove the edges and connected node.
                    tree.remove_edge(ed0[0],ed0[1]);
                    tree.remove_edge(ed1[0],ed1[1]);
                    tree.remove_node(nd);
                    
                    # Add the new edge.
                    segl = []; segl.append(sconn);
                    tree.add_edge(nb0,nb1,slist=segl);
                    print "** Added new edge from {0} to {1}, segment from {2} to {3} with path nodes from {4} to {5}".format(nb0,nb1,sconn.inode,sconn.fnode,sconn.path[0],sconn.path[-1]);
                    if(sconn.inode != nb0 or sconn.fnode != nb1):
                        print "[connect_tree] ERROR: adding invalid segment.";
                        exit();
                    
                    # Set true, as at least one connection was made.
                    connected = True;
                
    return connected;

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
for evt in range(evt_start,evt_end):

    # -------------------------------------------------------------------------
    # Read in the voxelized and MC tracks
    # -------------------------------------------------------------------------
    vtrk_file = "{0}/voxels_trk_{1}.dat".format(dat_base,evt);
    mctrk_file = "{0}/mctruehits_trk_{1}.dat".format(dat_base,evt);
    vtrk_file = mctrk_file
    print "hello",vtrk_file
    
    # If no file exists for this event, continue to the next.
    if(not os.path.isfile(vtrk_file) or not os.path.isfile(mctrk_file)):
        print vtrk_file
        print "File not found"
        continue
        
    # Read the voxelized track.
    trktbl = np.loadtxt(vtrk_file);
    vtrk_ID_temp = trktbl[:,0];
    vtrk_x = trktbl[:,1];
    vtrk_y = trktbl[:,2];
    vtrk_z = trktbl[:,3];
    vtrk_E = trktbl[:,4];
    if(debug > 0): print "Found {0} voxels".format(len(vtrk_ID_temp));

    # Convert to integer IDs.
    vtrk_ID = [];
    for vid in vtrk_ID_temp:
        vtrk_ID.append(int(vid));
    
    # Read the MC track.
    mctrktbl = np.loadtxt(mctrk_file);
    mctrk_ID_temp = mctrktbl[:,0];
    mctrk_x = mctrktbl[:,1];
    mctrk_y = mctrktbl[:,2];
    mctrk_z = mctrktbl[:,3];
    mctrk_E = mctrktbl[:,4];
    if(debug > 0): print "Found {0} voxels".format(len(mctrk_ID_temp));
    
    # Convert to integer IDs.
    mctrk_ID = [];
    for mid in mctrk_ID_temp:
        mctrk_ID.append(int(mid));
    
    # ---------------------------------------------------------------------------
    # Create the adjacency matrix
    # -1 --> self
    # 0 --> not a neighbor
    # (distance) --> voxels are neighbors
    # ---------------------------------------------------------------------------

    # Iterate through all voxels, and for each one find the neighboring voxels.
    adjMat = []; nnbrMat = []
    for vID1,vx1,vy1,vz1,vE1 in zip(vtrk_ID,vtrk_x,vtrk_y,vtrk_z,vtrk_E):
    
        nbr_list = [];
        nnbrs = 0;
        for vID2,vx2,vy2,vz2,vE2 in zip(vtrk_ID,vtrk_x,vtrk_y,vtrk_z,vtrk_E):
            
            if(vx1 == vx2 and vy1 == vy2 and vz1 == vz2):
                nbr_list.append(-1);
            else:
                #  AP 07/17/2015  use all links

                dist = sqrt((vx2-vx1)**2 + (vy2-vy1)**2 + (vz2-vz1)**2);
                if (dist < dist_cut):
                    nbr_list.append(dist);
                    nnbrs += 1;
                else:
                    nbr_list.append(0);

        nnbrMat.append(nnbrs);
        adjMat.append(nbr_list);


    if(debug > 3):
        print "Adjacency matrix:";
        print adjMat;

    # ---------------------------------------------------------------------------
    # Construct the graph for the track
    # ---------------------------------------------------------------------------
    
    trk = nx.Graph();
    print "  new trk  "
    print trk
    for vid in vtrk_ID:
        tnode = TrackNode(vid);
        trk.add_node(tnode);
        if (debug > 1 ):
            continue
            #print "vid,tnode",vid,tnode
    #print " Graph ",trk
    
    # Add edges connecting each node to its neighbor nodes based on the values
    #  in the adjacency matrix.
    n1 = 0;
    for nA in trk.nodes():
        
        n2 = 0;
        for nB in trk.nodes():
            ndist = adjMat[nA.id][nB.id];
            if(ndist > 0):
    #            print "Adding edge from {0} to {1}".format(n1,n2)
                trk.add_edge(nA,nB,weight=(ndist+0.000001*nA.id+0.000001*nB.id));
            n2 += 1;
                
        n1 += 1;

    if(debug > 2):
        #nx.draw_random(trk);
        #plt.show();
        print "    ******    trk.nodes    *******"
        #print trk.nodes()
        print "    -----     trk.edges    -------"
        #print trk.edges()

    # -------------------------------------------------------------------------
    #  Find the segments in the track.
    # -------------------------------------------------------------------------
    #nodes = find_nodes(trk,nnbrMat,vtrk_x,vtrk_y,vtrk_z);
    mst = nx.minimum_spanning_tree(trk);
    print "  =====    mst    ===="
    print mst
    segments = find_segments_mst(mst,adjMat,vtrk_x,vtrk_y,vtrk_z);
    if (debug > 0 ):
        print "\nSegments:";
        print segments;
        for seg in segments:
            print "  --------  segment ---------   "
            print seg.inode
            print seg.fnode
            print seg.length
            print "path ",seg.path
           
    # -------------------------------------------------------------------------
    #  Fill gaps in the determined segments.
    # -------------------------------------------------------------------------
##     segments_f = [];
##     for seg in segments: segments_f.append(seg);   #construct a list of found segments
##     print "  ============  segments ============   "
##     print segments_f
    
##     # Attempt to match endpoints of all segments.
##     for seg in segments:

##         ep1 = seg.inode;
##         print "-- Attempting to match endpoint {0}".format(ep1);
##         seg1 = match_to_segments(ep1,seg,segments_f,trk);
##         if(seg1 != 0): segments_f.append(seg1);
##             
##         ep2 = seg.fnode;
##         print "-- Attempting to match endpoint {0}".format(ep2);
##         seg2 = match_to_segments(ep2,seg,segments_f,trk);
##         if(seg2 != 0): segments_f.append(seg2);
##     print "  ============  segments  after matching ============   "
##     print segments_f   

    #  do not edit the tree   AP 07-21-2015 (comment the section above)
    
    t_nodes = []
    for seg in segments:
        if (seg.inode.type == 1):
            t_nodes.append(seg.inode)
        if (seg.fnode.type == 1):
            t_nodes.append(seg.fnode)
    print " terminal nodes"
    for tn in t_nodes:
        print tn.id
    
    tot_length = 0
    for seg in segments:
        tot_length += seg.length
    
    max_length = 0
    for i in range(len(t_nodes)):
        for j in range(len(t_nodes)):
            if (i<j):
                if ( debug > 1):
                    print "  pair of terminal nodes",i,j,t_nodes[i].id,t_nodes[j].id
                paths = nx.shortest_path(mst, source=t_nodes[i], target=t_nodes[j],weight='weight')
                plength = 0
                for nA,nB in zip(paths[:-1],paths[1:]):
                    #print nA.id,nB.id,adjMat[nA.id][nB.id]
                    plength += adjMat[nA.id][nB.id]
                if ( debug > 1 ):
                    print "  path length = ",plength
                if (plength>max_length):
                    max_length = plength
                    track_path = paths
    
    print "************************************************************************"
    print "total length of all segments ",tot_length, "longest path ",max_length
##     
##     for seg in segments:
##         ep1 = seg.inode
##         for seg1 in segments:
##             ep2 = seg1.inode
##             if(ep1.type==1 and ep2.type==1):
##                 print "path from ",ep1.id," to ",ep2.id
##                 paths = nx.shortest_path(mst, source=ep1, target=ep2,weight='weight')
##                 path_length = 0
##                 for nA,nB in zip(paths[:-1],paths[1:]):
##                     print nA.id,nB.id,adjMat[nA.id][nB.id]
##                     path_length += adjMat[nA.id][nB.id]
##                 print "  path length = ",path_length
##                 for path in paths:
##                     print path
##     
##     # -------------------------------------------------------------------------
##     #  Connect the determined segments.
##     # -------------------------------------------------------------------------    
##     connection = True;
##     segments_c = [];
##     for seg in segments_f: segments_c.append(seg);
##     print "   ----  segments_c   -----"
##     print segments_c
##     
##     while(connection):
##         
##         for cseg in segments_c:
##             
##             # Attempt to connect cseg with one or more segments in the list.
##             (connection,segments_c) = connect_segment_in_list(cseg,segments_c);
##             
##             # If a connection was made, break and restart the iteration.
##             if(connection):
##                 if(debug > 2): print "Connection made, restarting iteration...";
##                 break;
##                 
##     spaths = [];
##     for nseg in segments_c: spaths.append(nseg.path);

#    # -------------------------------------------------------------------------
#    #  Make connections by creating a graph out of the segments.
#    # -------------------------------------------------------------------------
#    # Create the graph.
#    sGraph = nx.Graph();
#    
#    for s1 in segments:
#
#        # Get the nodes belonging to the segment.
#        n1i = s1.inode;
#        n1f = s1.fnode;
#        
#        # Add nodes to the graph if they are not yet in the graph.
#        if(not sGraph.has_node(n1i)): sGraph.add_node(n1i);
#        if(not sGraph.has_node(n1f)): sGraph.add_node(n1f);
#        
#        # Add an edge to the graph corresponding to this segment.
#        if(sGraph.has_edge(n1i,n1f)):
#            segl = sGraph[n1i][n1f]['slist'];
#            segl.append(s1);
#            if(s1.inode != n1i or s1.fnode != n1f or s1.inode != s1.path[0] or s1.fnode != s1.path[-1]):
#                print "ERROR: adding invalid segment during main segment construction, multiple edges between same nodes.";
#                exit();
#            if(debug > 1): print "WARNING: graph already has an edge from nodes {0} to {1}; added seg from {2} to {3}".format(n1i,n1f,s1.inode,s1.fnode);
#        else:
#            segl = [];
#            segl.append(s1);
#            sGraph.add_edge(n1i,n1f,slist=segl);
#            if(debug > 1): print "Nodes {0} to {1}, added seg from {2} to {3}".format(n1i,n1f,s1.inode,s1.fnode);
#            if(s1.inode != n1i or s1.fnode != n1f or s1.inode != s1.path[0] or s1.fnode != s1.path[-1]):
#                print "ERROR: adding invalid segment during main segment construction.";
#                exit();
#
#    # "Prune" the graph by:
#    pruned = True;
#    while(pruned):
#        pruned = prune_tree(sGraph,15.0);
#        print "Pruning tree...";
#    print "Done pruning tree";
#    
#    #  Eliminate all remaining nodes with only two neighbors and combine
#    #     the segments connecting them into a single path.    
#    connected = True;
#    while(connected):
#        print "Connecting tree.";
#        connected = connect_tree(sGraph);
#
#    spaths = [];    
#    for edg in sGraph.edges():
#        
#        segl = sGraph[edg[0]][edg[1]]['slist'];
#        for seg in segl:
#            spaths.append(seg.path);

    ## ------------------------------------------------------------------------
    ## Plot the track.
    ## ------------------------------------------------------------------------







    # THREE WINDOWS !!!!!!!!!!!








    if(plot_trks):
        
        # Create plottable arrays of coordinates of voxels in the track.
#        vtrk_xf = []; vtrk_yf = []; vtrk_zf = [];
#        for vid in vtrk_ID:
#            vtrk_xf.append(vtrk_x[vid]);
#            vtrk_yf.append(vtrk_y[vid]);
#            vtrk_zf.append(vtrk_z[vid]);
        
        fig = plt.figure(1);
        fig.set_figheight(10.0);
        fig.set_figwidth(20.0);
        
        ax1= fig.add_subplot(131,projection='3d');
        colarr = ['red','green','blue','orange','black','violet'];
        npth = 1;
##         for pth in spaths:
##             xpth = []; ypth = []; zpth = [];            
##             for nn in pth:
##                 xpth.append(vtrk_x[nn.id]); ypth.append(vtrk_y[nn.id]); zpth.append(vtrk_z[nn.id]);
##             ax1.plot(xpth,ypth,zpth,'-',color=colarr[npth % len(colarr)]);
##             npth += 1;

        xpth = []; ypth = []; zpth = [];  
        for pts in track_path:
            #print pts
            #print vtrk_x[pts.id],vtrk_y[pts.id],vtrk_z[pts.id];
            xpth.append(vtrk_x[pts.id]); 
            ypth.append(vtrk_y[pts.id]); 
            zpth.append(vtrk_z[pts.id]);
        #print xpth
        #print ypth
        #print zpth
        ax1.plot(xpth,ypth,zpth,'-',color='red');

        
        
        ax1.set_xlabel("x (mm)");
        ax1.set_ylabel("y (mm)");
        ax1.set_zlabel("z (mm)");
        
        lb_x = ax1.get_xticklabels();
        lb_y = ax1.get_yticklabels();
        lb_z = ax1.get_zticklabels();
        for lb in (lb_x + lb_y + lb_z):
            lb.set_fontsize(8);
       
        ax2 = fig.add_subplot(132, projection='3d',sharex=ax1,sharey=ax1,sharez=ax1);
        colarr = ['red','green','blue','orange','black','violet'];
        npth = 0;
        for seg in segments:
            xpth = []; ypth = []; zpth = [];            
            for nn in seg.path:
                xpth.append(vtrk_x[nn.id]); ypth.append(vtrk_y[nn.id]); zpth.append(vtrk_z[nn.id]);
            ax2.plot(xpth,ypth,zpth,'-',color=colarr[npth % len(colarr)]);
            npth += 1;
        #ax2.plot(vtrk_x,vtrk_y,vtrk_z,'s',color='black');
        ax2.plot([mctrk_x[0]],[mctrk_y[0]],[mctrk_z[0]],'o',color='blue',markersize=5);
        ax2.plot([mctrk_x[-1]],[mctrk_y[-1]],[mctrk_z[-1]],'s',color='blue',markersize=5);
        ax2.set_xlabel("x (mm)");
        ax2.set_ylabel("y (mm)");
        ax2.set_zlabel("z (mm)");
        
        lb_x = ax2.get_xticklabels();
        lb_y = ax2.get_yticklabels();
        lb_z = ax2.get_zticklabels();
        for lb in (lb_x + lb_y + lb_z):
            lb.set_fontsize(8);

        colors = cm.rainbow(np.linspace(0, 1, len(mctrk_x)))       
        ax3 = fig.add_subplot(133, projection='3d',sharex=ax1,sharey=ax1,sharez=ax1);
        for px,py,pz,c in zip(mctrk_x,mctrk_y,mctrk_z,colors):
            #ax3.plot(1.,1.,1.,'s');
            ax3.plot([px],[py],[pz],'.',color=c,markersize=4);
        ax3.plot([mctrk_x[0]],[mctrk_y[0]],[mctrk_z[0]],'o',color='blue',markersize=5);
        ax3.plot([mctrk_x[-1]],[mctrk_y[-1]],[mctrk_z[-1]],'s',color='blue',markersize=5);
        ax3.set_xlabel("x (mm)");
        ax3.set_ylabel("y (mm)");
        ax3.set_zlabel("z (mm)");
        
        lb_x = ax3.get_xticklabels();
        lb_y = ax3.get_yticklabels();
        lb_z = ax3.get_zticklabels();
        for lb in (lb_x + lb_y + lb_z):
            lb.set_fontsize(8);
        #linkprop([ax1],'CameraPosition')
#        ax1.plot(vtrk_xf,vtrk_yf,vtrk_zf,'s',color='blue');
#        ax1.plot([vtrk_x[vinit]],[vtrk_y[vinit]],[vtrk_z[vinit]],'o',color='green',markersize=15)
#        ax1.plot([vtrk_x[vfinal]],[vtrk_y[vfinal]],[vtrk_z[vfinal]],'x',color='green',markersize=15)
        
#        # Plot the nodes.
#        nxvals = []; nyvals = []; nzvals = [];
#        for nd in nodes:
#            nxvals.append(vtrk_x[nd]); 
#            nyvals.append(vtrk_y[nd]); 
#            nzvals.append(vtrk_z[nd]);
#        ax1.plot(nxvals,nyvals,nzvals,'o',color='red',markersize=15);
        
##         if(print_trks):
##             fn_plt = "{0}/trk_segments_{1}_{2}.{3}".format(plt_base,evt_type,evt,out_fmt);
##             plt.savefig(fn_plt, bbox_inches='tight');
##         else:
##             plt.show();
            plt.show()
    
# ---------------------------------------------------------------------------
# Find the extrema
# ---------------------------------------------------------------------------
#vinit,vfinal = find_extremes_EoverN(trk,10.,10,vtrk_ID,vtrk_x,vtrk_y,vtrk_z,vtrk_E);
#vinit,vfinal = find_extremes_Paolina(trk);

## Iterate through all voxels to find the maximum energy blob.
#eblob_max = -1; vblob_max = -1
#for vID1,vx1,vy1,vz1,vE1 in zip(vtrk_ID,vtrk_x,vtrk_y,vtrk_z,vtrk_E):
#
#    # For this voxel, calculate the blob energy.
#    eblob = 0;
#    for vID2,vx2,vy2,vz2,vE2 in zip(vtrk_ID,vtrk_x,vtrk_y,vtrk_z,vtrk_E):
#        if(sqrt((vx2-vx1)**2 + (vy2-vy1)**2 + (vz2-vz1)**2) < blob_radius):
#              eblob += vE2;
#    
#    if(eblob > eblob_max):
#        eblob_max = eblob;
#        vblob_max = vID1;
#
## Iterate through all voxels to find the one with the longest shortest path
##  from the center of the maximum blob.
#max_short = -1; vlong_short = -1;
#for vID1,vx1,vy1,vz1,vE1 in zip(vtrk_ID,vtrk_x,vtrk_y,vtrk_z,vtrk_E):
#    #pth = nx.astar_path(trk,vblob_max,vID1);
#    pth = nx.shortest_path(trk,vblob_max,vID1,"weight");
#    plen = len(pth);
#    if(plen > max_short):
#        max_short = plen;
#        vlong_short = vID1;
#
#if(debug > 0):
#    print "Found blob at voxel {0}, beginning of track at voxel {1}".format(vblob_max,vlong_short);

### ---------------------------------------------------------------------------
### Step through the track, favoring directions along the way of the present momentum
### ---------------------------------------------------------------------------
#ftrack = [];
#
## Create a matrix of booleans for the visited voxels.
#visitedMat = [];
#for n1 in range(len(vtrk_ID)):
#    visitedMat.append(False);
#
## -----------------------------------------------------------------------------
## Traverse the graph according to the following rules:
## 1. proceed to the next neighbor in which the direction is closest to
##   the present momentum direction (initial momentum direction in random)
## 2. only proceed to the next neighbor if it is unvisited, or jump a single
##    neighbor to one of its unvisited neighbors
## 3. end when the 2nd extreme has been reached, or no longer possible to
##    proceed to the next node
#done = False;
#curr_vox = vinit;
#curr_p = np.array([0,0,0]);
#ftrack.append(curr_vox);
#visitedMat[curr_vox] = True;
#
## Get one of the neighbors of the first vector at random.
#nbrs_init = [];
#inbr = 0;
#for nval in adjMat[vinit]:
#    if(nval > 0): nbrs_init.append(inbr);
#    inbr += 1;
#if(len(nbrs_init) > 0):
#    rnbr = nbrs_init[np.random.randint(len(nbrs_init))];
#    curr_p = dir_vec(vtrk_x[vinit],vtrk_y[vinit],vtrk_z[vinit],vtrk_x[rnbr],vtrk_y[rnbr],vtrk_z[rnbr]);
#    curr_vox = rnbr;
#    ftrack.append(curr_vox);
#    visitedMat[curr_vox] = True;
#    if(debug > 1):
#        print "Initial step to voxel {0} with direction ({1},{2},{3})".format(curr_vox,curr_p[0],curr_p[1],curr_p[2]);
#else:
#    print "No neighbors found for initial voxel.";
#    done = True;
#    
## Set up the momentum queue to average the past npavg momenta.
#pq = deque(maxlen=npavg);
#pq.appendleft(curr_p);
#
## Continue searching through all other voxels.
#while(not done):
#    
#    # Ensure we have not reached the final voxel.
##    if(curr_vox == vfinal):
##        if(debug > 1): print "[Voxel {0}]: END (final voxel reached)".format(curr_vox);
##        done = True;
##        break;
#    
#    # Get the neighbor vector for this voxel.
#    nmat = adjMat[curr_vox];
#    
#    # Get all visitable neighbors with priority 1 and 2.
#    #  Note: priority 1 is preferred over priority 2
#    nids1 = []; nids2 = [];
#    inbr = 0;
#    for nval in nmat:
#        
#        # Neighbor found if nonzero value in adjacency matrix.
#        if(nval > 0):
#            # Neighbor is priority 1 if not visited.
#            if(not visitedMat[inbr]):
#                nids1.append(inbr);
#            # Neighbor is priority 2 if visited but contains unvisited neighbors.
#            else:
#                pri2 = False;
#                nmat2 = adjMat[inbr];
#                inbr2 = 0;
#                for nval2 in nmat2:                    
#                    # Make this neighbor priority 2 if it has at least 1 non-visited neighbor.
#                    if(nval2 > 0 and not visitedMat[inbr2]): 
#                        pri2 = True;
#                        break;
#                    inbr2 += 1;
#                if(pri2): nids2.append(inbr);
#        inbr += 1;
#        
#    max_dot = -2.; nmax_dot = -1; next_vox = -1;
#    if(len(nids1) > 0):
#        for nbr1 in nids1:
#            dvec = dir_vec(vtrk_x[curr_vox],vtrk_y[curr_vox],vtrk_z[curr_vox],vtrk_x[nbr1],vtrk_y[nbr1],vtrk_z[nbr1]);
#            dprod = curr_p[0]*dvec[0] + curr_p[1]*dvec[1] + curr_p[2]*dvec[2];
#            if(dprod > max_dot):
#                max_dot = dprod; nmax_dot = nbr1;
#        next_vox = nbr1;
#    elif(len(nids2) > 0):
#        for nbr2 in nids2:
#            dvec = dir_vec(vtrk_x[curr_vox],vtrk_y[curr_vox],vtrk_z[curr_vox],vtrk_x[nbr2],vtrk_y[nbr2],vtrk_z[nbr2]);
#            dprod = curr_p[0]*dvec[0] + curr_p[1]*dvec[1] + curr_p[2]*dvec[2];
#            if(dprod > max_dot):
#                max_dot = dprod; nmax_dot = nbr2;
#        next_vox = nbr2;
#    else:
#        if(debug > 1): print "[Voxel {0}]: END (no neighbors)".format(curr_vox);
#        done = True;
#        break;
#    
#    # Set the next voxel as the current voxel, and add it to the track.
#    if(debug > 1): print "-- [Voxel {0}, p = ({1},{2},{3})] Adding next voxel {4} to track".format(curr_vox,curr_p[0],curr_p[1],curr_p[2],next_vox);
#    new_p = dir_vec(vtrk_x[curr_vox],vtrk_y[curr_vox],vtrk_z[curr_vox],vtrk_x[next_vox],vtrk_y[next_vox],vtrk_z[next_vox]);
#    nptemp = 1;
#    for old_p in pq:
#        new_p += old_p;
#        nptemp += 1;
#    new_p /= nptemp;
#    print "Averaged {0} momenta values".format(nptemp);
#    
#    # Set and record the current momentum.
#    curr_p = new_p;
#    pq.appendleft(new_p);
#    curr_vox = next_vox;
#    ftrack.append(curr_vox);
#    visitedMat[curr_vox] = True;
#
#print ftrack;

## ---------------------------------------------------------------------------
## Find all paths between each pair of nodes.
## ---------------------------------------------------------------------------
#
#print "Finding longest path...";
#pth = longest_path(trk);
#print pth;
#
#print "Finding shortest path...";
##pth = nx.astar_path(trk,0,190);
#pth = nx.all_simple_paths(trk,0,190);
#print(list(pth))


#print "\n\n ** Begin path finding ** \n\n";
#
#lmax = 0; max_path = []
#for n1 in trk.nodes():
#    
#    for n2 in trk.nodes():
#        if(debug > 1): print "-- Finding paths between nodes {0} and {1}".format(n1,n2);
#        
#        if(n1 != n2):
#            for pth in nx.all_simple_paths(trk,source=n1,target=194,cutoff=20):
#                lpth = len(pth);
#                print "--> Found path of length {0}".format(lpth);
#                if(lpth > lmax):
#                    max_path = pth;
#                    lmax = lpth;
                
#print "Found max. path of length {0}:".format(lmax);
#print max_path;

## Set up the figure.
#fig = plt.figure();
#fig.set_figheight(5.0);
#fig.set_figwidth(7.5);
#
## xy-coordinates for plotting polynomials.
#xplot = np.linspace(min(qS1c_avals),max(qS1c_avals),100);
#
## Make the S1 vs. S2 histogram
#hs1s2, xs1s2, ys1s2 = np.histogram2d(qS1c_avals, qS2_avals, bins=(nbins_2d, nbins_2d), range=[[-5.,max(qS1c_avals)],[-800.,max(qS2_avals)]]);
#x = 0.5*(xs1s2[:-1] + xs1s2[1:]);
#y = 0.5*(ys1s2[:-1] + ys1s2[1:]);
#extent = [ys1s2[0], ys1s2[-1], xs1s2[0], xs1s2[-1]];
#Y,X = np.meshgrid(y,x);
##hs1s2[hs1s2 == 0] = 1;
##hs1s2 = np.log10(hs1s2);
##extent = [ys1s2[0], ys1s2[-1], xs1s2[0], xs1s2[-1]];
##plt.imshow(hs1s2, extent=extent, interpolation='none', aspect='auto', origin='lower');
##plt.plot(xfit_vals,mufit_vals,'--',color='r',linewidth=2);
#if(scatter_plt):
#    plt.plot(qS1c_avals,qS2_avals,'.',color='black',markersize=3.0);
#else:
#    plt.contourf(X,Y,hs1s2,cmap=tc_gs_cmap);
#    plt.plot(xplot,p0(xplot),'-',color='black',linewidth=2);
#    plt.plot(xplot,p1(xplot),'--',color='black',linewidth=2);
#    plt.plot(xplot,p2(xplot),'--',color='black',linewidth=2);
#    #plt.plot(xplot,p3(xplot),'-',color='black',linewidth=2);
#    #plt.plot(xplot,p4(xplot),'--',color='black',linewidth=2);
#    #plt.plot(xplot,p5(xplot),'--',color='black',linewidth=2);
#    #plt.plot(xfit_vals,mufit_vals,'.',color='black');
#    #plt.plot(xfit_vals,mu2msigma_vals,'.',color='black');
#    plt.annotate('Xe x-rays', xy=(20, 25000),  xycoords='data',
#                 xytext=(36, 28000), textcoords='data', arrowprops=dict(arrowstyle="-"));
#    plt.annotate('', xy=(17, 28000),  xycoords='data',
#                 xytext=(36, 28000), textcoords='data', arrowprops=dict(arrowstyle="-"));
#    plt.annotate('$^{129}$Xe inelastics', xy=(30, 35000),  xycoords='data',
#                 xytext=(43, 34000), textcoords='data', arrowprops=dict(arrowstyle="-"));
#    plt.annotate('Nuclear recoils', xy=(15, 8000),  xycoords='data',
#                 xytext=(43, 4000), textcoords='data', arrowprops=dict(arrowstyle="-"));
#    plt.colorbar();
##plt.plot(xplot,p0(xplot),'-.',color='black',linewidth=2);
##plt.vlines([x_fitmin,x_fitmax],0,y_fitmax,linestyle='-.',color='black',linewidth=1);
##plt.hlines(y_fitmax,x_fitmin,x_fitmax,linestyle='-.',color='black',linewidth=1);
#plt.xlabel("S1 (photons,corrected)",fontsize=tc_lfont_size);
#plt.ylabel("S2 (photons)",fontsize=tc_lfont_size);
##fig.text(fig_xlabel,0.2,fig_text,color='white',fontsize=1.4*tc_tlabel_size);
##plt.axis([xs1s2[0],xs1s2[-1],ys1s2[0],ys1s2[-1]]);
#plt.axis([0,60,0,48000]);
#formatPlot(plt);
#plt.savefig(fig_name, bbox_inches='tight');
#plt.show();


## Prune a tree (remove dangling edges)
##  Find all of the nodes with only one neighbor, and eliminate the
##     corresponding segments if they are not long enough.
#def prune_tree(tree,plen):
#    
#    # Return false if nothing is pruned from the tree.
#    pruned = False;
#
#    # Iterate through the nodes, identifying edges that should be pruned.
#    for nd in tree.nodes():
#        
#        edges = tree.edges(nd);
#        if(debug > 2): print "Got {0} edges for node {1}".format(len(edges),nd);
#        
#        if(len(edges) == 1):
#            ed = edges[0];
#            segl = tree[ed[0]][ed[1]]['slist'];
#
#            if(len(segl) == 1):
#                edg_len = segl[0].length;
#                if(debug > 2): print "Got single segment with length {0}".format(edg_len);
#                
#                if(edg_len < plen):
#                    if(debug > 2): print "Removing node {0}".format(nd);
#                    tree.remove_edge(ed[0],ed[1]);
#                    tree.remove_node(nd);
#                    pruned = True;
#                
#        elif(len(edges) == 2):
#            ed0 = edges[0]; segl0 = tree[ed0[0]][ed0[1]]['slist']; 
#            ed1 = edges[1]; segl1 = tree[ed1[0]][ed1[1]]['slist'];
#            
#            # Only proceed if we don't have multiple segments per node pair.
#            if(len(segl0) == 1 and len(segl1) == 1):
#                
#                edg_len0 = segl0[0].length;
#                edg_len1 = segl1[0].length;
#                if(debug > 2): print "Got two segments with lengths {0} and {1}".format(edg_len0,edg_len1);
#                            
#                # Remove the two edges if both are less than plen in length and there
#                #  exists an edge between the two neighbors.            
#                if(edg_len0 < plen and edg_len1 < plen):
#                    nb0 = ed0[0];
#                    if(nb0 == nd): nb0 = ed0[1];
#                    nb1 = ed1[0];
#                    if(nb1 == nd): nb1 = ed1[1];
#                    
#                    if(tree.has_edge(nb0,nb1)):
#                        print "Removing node {0}".format(nd);
#                        tree.remove_edge(ed0[0],ed0[1]);
#                        tree.remove_edge(ed1[0],ed1[1]);
#                        tree.remove_node(nd);
#                        pruned = True;
#                
#    return pruned;
