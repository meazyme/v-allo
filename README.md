# v-allo
Allocate regional data (e.g. energy demands) to points (e.g. network nodes) using Voronoi/Thiessen polygons as closeness factor.

In a set of finitely many points in the plane (called seeds, sites, or generators), for each seed there is a corresponding region, called a Voronoi cell, consisting of all points of the plane closer to that seed than to any other. When creating these cells for all seeds, you get a Voronoi diagram.

![Voronoi_growth_euclidean](https://user-images.githubusercontent.com/88534161/181002526-64645ae0-2f5f-4ab2-8d85-de9eb7d00174.gif)
(source: Wikepedia.org)

v-allo creates this diagram for you and allows you to overlay the created voronoi polygons with other shapes in order to find what percentage of each shape is covered by wich node. This can be useful for many applications, e.g. energy demands mapped to network nodes. 

When you just need the diagram, run create_voronoi_diagram and map_polys_to_nodes.

For overlaying with other geodata to get distribution keys as described above, run the functions named above and then find_prop_of_area.

v-allo is based mainly on shapely, geopandas and scipy.spatial.Voronoi


TODO:
- test allocation with extra weights
- allow passing different distance function to voronoi
- speed up map_polys_to_nodes
