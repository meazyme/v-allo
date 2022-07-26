from voronoi import show, create_voronoi_diagram, map_polys_to_nodes, find_prop_of_area, check_plausibility
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from random import uniform


def allocate():
    pass


if __name__ == '__main__':
    # get some data (random points)
    nodes_gdf = gpd.GeoDataFrame(geometry=[Point(uniform(6, 15), uniform(47, 55)) for _ in range(50)],
                                 data={'node_id': [str(i) for i in range(50)]})
    nodes_gdf.crs = 'epsg:4326'  # points should be crs aware when intersection with geodata
    # needs to have nodes as shapely Points

    # create the polygons around the node
    voro_gdf = create_voronoi_diagram(nodes_gdf, buffer=10)
    # it is very important to choose the right buffer, such that the bounding box for the polygons will not be smaller
    # than the regions' furthest extend. If the graph 'Intersection of administrative regions and voronoi polygons'
    # does not include all of the regions expected when looking at results, increase the buffer until all are included.
    # The buffer size will also depend heavily on the CRS used.

    # map voronoi polygons to nodes
    voro_gdf = map_polys_to_nodes(voro_gdf, nodes_gdf, point_id='node_id')

    # check whether polygons and nodes are overlapping as expected
    show('Polygons and corresponding nodes', voro_gdf, nodes_gdf)

    # get some geodata for overlaying with the voronoi diagram
    regions_gdf = gpd.read_file('germany_nuts2_example/germany_nuts2_example.shp')
    regions_gdf.crs = 'epsg:3035'
    # needs to have regions as shapely Polygons or MultiPolygons

    # intersect the voronoi polygons and nuts3 regions to get the allocation key
    # specify a common projection that will be applied to both geo-dataframes before overlaying
    results_df, intersect_gdf = find_prop_of_area(voro_gdf, regions_gdf,
                                                  region_id='NUTS_ID', point_id='node_id',
                                                  common_projection=3035)
    check_plausibility(results_df, voro_gdf, nodes_gdf, regions_gdf, intersect_gdf,
                       show_plots=True, region_id='NUTS_ID', point_id='node_id',
                       common_projection=3035)
    # get some demand data
    # regional_demand_df = ...  # needs to have same region ids as regions_gdf and demand per region

    # results = allocate()
