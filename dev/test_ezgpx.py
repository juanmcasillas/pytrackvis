import ezgpx
import matplotlib

# Parse GPX file
gpx = ezgpx.GPX("../data/gpx/garmin-fenix3-running.gpx")

# Simplify (using Ramer-Dougle-Peucker algorithm)
#gpx.simplify()
# Remove metadata
#gpx.remove_metadata()

# Plot with Matplotlib
gpx.matplotlib_plot(figsize=(16,9),
                         size=6,
                         color="yellow",
                         #color="ele",
                         #cmap=matplotlib.colormaps.get_cmap("gnuplot"),
                         colorbar=False,
                         start_point_color="green",
                         stop_point_color="red",
                         way_points_color=None,
                         background="World_Imagery",
                         offset_percentage=0.04,
                         dpi=100,
                         title=gpx.name(),
                         title_fontsize=20,
                         watermark=True,
                         file_path="img_1.png")

# gpx.expert_plot(figsize=(16,9),
#                      subplots=(3,2),
#                      map_position=(0,0),
#                      map_size=10,
#                      map_color="ele",
#                      map_cmap=matplotlib.colormaps.get_cmap("viridis"),
#                      map_colorbar=True,
#                      start_point_color=None,
#                      stop_point_color=None,
#                      way_points_color=None,
#                      background="World_Imagery",
#                      offset_percentage=0.04,
#                      xpixels=1000,
#                      ypixels=None,
#                      dpi=100,
#                      elevation_profile_position=(1,0),
#                      elevation_profile_size=10,
#                      elevation_profile_color="ele",
#                      elevation_profile_cmap=matplotlib.colormaps.get_cmap("viridis"),
#                      elevation_profile_colorbar=False,
#                      elevation_profile_grid=True,
#                      elevation_profile_fill_color="lightgray",
#                      elevation_profile_fill_alpha=0.5,
#                      pace_graph_position=(2,0),
#                      pace_graph_size=10,
#                      pace_graph_color="ele",
#                      pace_graph_cmap=None,
#                      pace_graph_colorbar=False,
#                      pace_graph_grid=True,
#                      pace_graph_fill_color="lightgray",
#                      pace_graph_fill_alpha=0.5,
#                      pace_graph_threshold=15,
#                      ascent_rate_graph_position=(1,1),
#                      made_with_ezgpx_position=(0,1),
#                      shared_color="ele",
#                      shared_cmap=None,
#                      shared_colorbar=True,
#                      data_table_position=(2,1),
#                      title=gpx.name(),
#                      title_fontsize=20,
#                      watermark=False,
#                      file_path="img_1.png")

# Write new simplified GPX file
#gpx.to_gpx("new_file.gpx")