import folium
m = folium.Map(location=(40.360986, -4.392448),
               tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
               attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
              )
    #folium.PolyLine(points, color='yellow', weight=4.5, opacity=.8).add_to(mymap)
m.save("index.html")