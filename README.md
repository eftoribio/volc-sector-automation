# PyQGIS Script for Automating Volcano Base Sectorization

This script merges, splits, rotates, and intersects shapefiles to automate the sectorization of volcano bases. The method used is based on [Voros et al. (2022)](https://doi.org/10.3390/rs13101983).

This was developed for my undergraduate thesis. For more information visit the [data visualization repo](https://github.com/eftoribio/volc-sector-automation).

## Prerequisites
- Folder named *split_indiv_points* containing individual point shapefiles of volcano summit locations
- Polygon shapefile of volcano bases named *rois_merged*
- Azimuth of the maximum base diameter that passes through the summit point stored as *AzimAxisBa*
- Slope raster from which zonal statistics will be computed
## Description
First, the path to the folder containing the individual summit point shapefiles is defined. A for-loop walks through all the shapefiles in the folder and append each file to a list.

A nested for-loop then iterates over each shapefile in the list, adding each point to QGIS as a vector layer. The first for-loop within this nested for-loop obtains the azimuth of the maximum base diameter that passes through the summit point (AzimAxisBaseMax). This is a parameter that should already be present in the shapefiles' *AzimAxisBa* field. The second for-loop creates the sectors one-by-one using the Create Wedge Buffers tool of QGIS and is based on the code of Lucchese (2022).

According to Vörös et al. (2021), each sector should have a size of 15 degrees because if it were too large, the difference from the whole-edifice value would not be appreciated. If the sector size were too small, there would be too many sectors whose values would be greatly influenced by any small changes. Thus, the for-loop creates 24 wedge-shaped polygons in total, and adds a *sectornumber* field, numbering each sector from 1 to 24 in counterclockwise direction.

The sectors are also rotated such that the centerline coincides with the maximum base diameter that passes through the summit point. All these sectors are merged into one shapefile and split into separate shapefiles according to volcano name.

The result is one polygon shapefile containing the sectorized volcano edifice outlines with each sector having its respective sectorial mean, median, majority, minimum, and maximum listed in the attribute table.

## References
*Lucchese, L. (2022). Generates "numsectors" circular sectors with the same width and varying radius [Source code]. https://gist.githubusercontent.com/luisalucchese/a8265f1247e770d832db806b853d8660/raw/6f8c4696a8a230f395163dc86c0abad0e98ebd95/examples_wedge_sectors_radius.py*
*Vörös, F., van Wyk de Vries, B., Karátson, D., & Székely, B. (2021). DTM-Based Morphometric Analysis of Scoria Cones of the Chaîne des Puys (France)—The Classic and a New Approach. Remote Sensing, 13(10), 1983. https://doi.org/10.3390/rs13101983*
*
## License

[MIT](https://github.com/eftoribio/volc-sector-automation/blob/main/LICENSE)
