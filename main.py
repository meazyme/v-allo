from voronoi import show, create_voronoi_diagram, map_polys_to_nodes, find_prop_of_area, check_plausibility, allocate
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from random import uniform


def voronoi_diagram(seeds: gpd.GeoDataFrame, buffer: int, point_id: str, show_plots=True) -> gpd.GeoDataFrame:
    """
    Create a Voronoi Diagram from a set of seeds. TODO: allow distance functions other than euclidean

    :param seeds: GeoDataFrame with the seeds for the voronoi diagram as geometry column in the shapely Point format.
    :param buffer: A bounding box will be created around the seeds (otherwise the outer cells will be infinite).
        Depending on the CRS used, the appropriate buffer size can vary a lot and should be tested.
    :param point_id: Column name that includes the IDs of the seeds (each seed should have a unique identifier).
    :param show_plots: Allow/Disallow plotting.
    :return: GeoDataFrame with the Voronoi cells as 'geometry' column in the format of shapely Polygons
        and a column containing the seed IDs.
    """
    # create the diagram and map the polygons to corresponding  nodes
    voro = create_voronoi_diagram(seeds, buffer=buffer)
    voro = map_polys_to_nodes(voro, seeds, point_id=point_id)
    # check whether polygons and nodes are overlapping as expected
    if show_plots:
        show('Polygons and corresponding nodes', voro, seeds)
    return voro


def voronoi_allocation(seeds: gpd.GeoDataFrame, demand: pd.Series, voro: gpd.GeoDataFrame, regions: gpd.GeoDataFrame,
                       region_id: str, point_id: str, common_proj: int, extra_weight=None, show_plots=True):
    """
    After creating the Voronoi Diagram, you can use it to allocate regional data to the seeds using the intersection
    area of the Voronoi cells with the regions as distribution keys. An additional distribution key is allowed.

    :param seeds: GeoDataFrame with the seeds for the voronoi diagram as geometry column in the shapely Point format.
    :param demand: Series with the region IDs as index and the demand as values.
    :param voro: GeoDataFrame as returned by voronoi_diagram().
    :param regions: GeoDataFrame with the regions as shapely Polygons/MultiPolygons in  the geometry column.
    :param region_id: Column name used to uniquely identify regions.
    :param point_id: Column name to uniquely identify nodes / seeds.
    :param common_proj: CRS to be applied to regions and seeds/voronoi diagram before intersection.
        3035 recommended for Europe, as it has little distortion.
    :param extra_weight: Pass an additional allocation weight / key. Format: Series with point_id as index.
    :param show_plots: Allow/Disallow plotting.
    :return: Series with point ID as index and allocated data as values.
    """

    distribution_table, intersection = find_prop_of_area(voro, regions, region_id=region_id, point_id=point_id,
                                                         common_projection=common_proj)
    check_plausibility(distribution_table, voro, seeds, regions, intersection,
                       show_plots=show_plots, region_id=region_id, point_id=point_id)
    allocated = allocate(distribution_table, demand, extra_weight=extra_weight)
    return allocated


if __name__ == '__main__':
    # EXAMPLE USE CASE

    # get some data (random points)
    nodes_gdf = gpd.GeoDataFrame(geometry=[Point(uniform(6, 15), uniform(47, 55)) for _ in range(50)],
                                 data={'node_id': [str(i) for i in range(50)]})
    nodes_gdf.crs = 'epsg:4326'  # points should be crs aware when intersection with geodata
    # get some geodata for overlaying with the voronoi diagram
    regions_gdf = gpd.read_file('germany_nuts2_example/germany_nuts2_example.shp')
    regions_gdf.crs = 'epsg:3035'
    # get some random demand data
    demands = pd.Series(index=regions_gdf.NUTS_ID, data=[uniform(0, 100) for r in regions_gdf.NUTS_ID])

    # TOOL APPLICATION:
    voronoi = voronoi_diagram(seeds=nodes_gdf, buffer=10, point_id='node_id', show_plots=True)
    allo = voronoi_allocation(seeds=nodes_gdf, demand=demands, voro=voronoi, regions=regions_gdf, region_id='NUTS_ID',
                              point_id='node_id', common_proj=3035, extra_weight=None, show_plots=True)

    print(f'{demands.sum()}')
    print(f'{allo.sum()}')
