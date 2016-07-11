#graphtest.py

##Tests graph algorithms for voxelized tracks

Notes:

 - the networkx package does not preserve the node ordering nodes in unordered
   graphs are expected to be such that the order doesn't matter
 - there could be multiple MSTs, and this is likely when using voxels
   because the distances are discrete (temporary fix, add some negligible
   distance varying based on voxel ID number) also in MST traversal begin
   with a node that has only 1 neighbor - as there are likely to be multiple,
   begin with the one that has lowest voxel ID

   * results do vary based on how the tree is traversed and where the starting
     node is

    current problems: (07/23/2015)  62, (68), (69), (71), (75), 81, (82??),
                                    83, 90,94,116,126,148
@author: josh, Thomas Hein, & Nate

----

To do:
-  treat the Monte Carlo information (point ordering)
   for double beta decay events

----

History:

- 08/11/2015
 - remove nnbrMat references
 - change distance to -1 for remote hits (it was 0)
 - make waight of the link equal to the distance of hits
- 07/11/2016
 - See commit history