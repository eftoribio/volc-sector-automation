import os
from PyQt5.QtCore import QVariant

# Define path to folder containing shapefiles
shapefolder = r'D:/Documents/2nd Sem/Geol 200/split_indiv_points'

# Create empty list to hold shapefile paths
shapeList = []

# Walk through all files in shapefolder (including subdirectories)
for root, folder, files in os.walk(shapefolder):
    for file in files: 
        # Find shapefiles
        if file.endswith('.shp'):
            # Combine path and filename
            fullname=os.path.join(root, file)
            # Add to shapeList
            shapeList.append(fullname)

# For each shapefile, create a vector layer and add it to the map
for index, shapefile in enumerate(shapeList):
    shapefile = shapefile.replace("\\", "/")
    layer_name = 'centroid_' + str(index)
    vlayer = QgsVectorLayer(shapefile, layer_name, "ogr")
    QgsProject.instance().addMapLayer(vlayer)
    
    # Get AzimAxisBa value for each feature in the layer
    for feature in vlayer.getFeatures():
        AzimAxisBa = feature["AzimAxisBa"]
    
    # Create wedges for each sector and add them to the map
    # Code in the next 7 lines is based on work by Luisa V. Lucchese (2022) https://gist.github.com/luisalucchese/36dc6fed3cb7800c79c9870e12a17426#file-examples_wedge_sectors-py
    numsectors=24
    width=360.0/numsectors
    for k in range(0,numsectors):
        azim=float(AzimAxisBa)+width/2+k*width
        paramwedge={ 'AZIMUTH' : azim, 'INNER_RADIUS' : 0, 'INPUT' : shapefile, 'OUTER_RADIUS' : 1000, 'OUTPUT' : 'memory:' , 'WIDTH' : width} 
        layer_wedge=processing.run("native:wedgebuffers", paramwedge)
        QgsProject.instance().addMapLayer(layer_wedge['OUTPUT'])
        
        # Add a sector attribute to each wedge
        pr = layer_wedge['OUTPUT'].dataProvider()
        pr.addAttributes([QgsField("sector",QVariant.Int)])
        layer_wedge['OUTPUT'].updateFields()
        layer_wedge['OUTPUT'].startEditing()
        for f in layer_wedge['OUTPUT'].getFeatures():
            id = f.id()
            sectornumber = 24 - k
            attr_value={10:sectornumber}
            pr.changeAttributeValues({id:attr_value})
            layer_wedge['OUTPUT'].commitChanges()

# Merge all wedge layers into a single layer
listLayers = QgsProject.instance().mapLayersByName('output')
processing.runAndLoadResults("native:mergevectorlayers", {'LAYERS': listLayers,'CRS':None,'OUTPUT':'D:/Documents/2nd Sem/Geol 200/split_centroids/merged/Merged.shp'})

# First, we merge all output shapefiles into one
listLayers = QgsProject.instance().mapLayersByName('output')
processing.runAndLoadResults("native:mergevectorlayers", 
    {'LAYERS': listLayers,'CRS':None,'OUTPUT':'D:/Documents/2nd Sem/Geol 200/split_centroids/merged/Merged.shp'})

# Next, we split the merged shapefile by the CLASS_NAME attribute
processing.run("native:splitvectorlayer", 
    {'INPUT':'D:/Documents/2nd Sem/Geol 200/split_centroids/merged/Merged.shp',
     'FIELD':'CLASS_NAME',
     'FILE_TYPE':1,
     'OUTPUT':'D:/Documents/2nd Sem/Geol 200/split_centroids/split_sectors'})

# Then, we search for all shapefiles in the split_sectors folder and add them to the QGIS project
shapefolder = r'D:/Documents/2nd Sem/Geol 200/split_centroids/split_sectors'
shapeList = []
for root, folder, files in os.walk(shapefolder):
    for file in files: # For all files in shapefolder, including files in subdirectories
        if file.endswith('.shp'): # Find the shapefiles
            fullname=os.path.join(root, file) # Combine path and filename
            shapeList.append(fullname)

for index, shapefile in enumerate(shapeList):
    shapefile = shapefile.replace("\\", "/")
    vlayer = QgsVectorLayer(shapefile, "rotated", "ogr")
    QgsProject.instance().addMapLayer(vlayer)

# We then merge all rotated shapefiles into one
listRotated = QgsProject.instance().mapLayersByName('rotated')
processing.runAndLoadResults("native:mergevectorlayers", 
    {'LAYERS': listLayers,'CRS':None,'OUTPUT':'D:/Documents/2nd Sem/Geol 200/split_centroids/merged/Rotated_Merged.shp'})

# After that, we perform an intersection between the rotated merged shapefile and rois_merged shapefile
processing.runAndLoadResults("native:intersection",
    {'INPUT': 'D:/Documents/2nd Sem/Geol 200/split_centroids/merged/Rotated_Merged.shp',
     'OVERLAY':'D:/Documents/2nd Sem/Geol 200/rois_merged.shp',
     'INPUT_FIELDS':[],
     'OVERLAY_FIELDS':[],
     'OVERLAY_FIELDS_PREFIX':'',
     'OUTPUT':'D:/Documents/2nd Sem/Geol 200/split_centroids/merged/rois_intersected.shp'})

# Lastly, we compute zonal statistics for the intersected shapefile and the macolod_slope raster
processing.runAndLoadResults("native:zonalstatisticsfb", 
    {'INPUT':'D:/Documents/2nd Sem/Geol 200/split_centroids/merged/rois_intersected.shp',
     'INPUT_RASTER':'D:/Documents/2nd Sem/Geol 200/macolod_slope',
     'RASTER_BAND':1,
     'COLUMN_PREFIX':'sector_',
     'STATISTICS':[2,3,4,5,6,7],
     'OUTPUT':'D:/Documents/2nd Sem/Geol 200/split_centroids/merged/zonalstatistics.shp'})
