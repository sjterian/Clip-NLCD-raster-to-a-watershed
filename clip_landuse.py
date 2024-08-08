####################### Watershed Land Use Percentages Calculator #####################

# This code lets you specify a given watershed and calculate the percentages of each land use type in that watershed.
# This code will export the following:
#       a csv file that has the percentages broken down by land use type, 
#       a land use raster clipped to the watershed, 
#       a shapefile of the selected watershed


# Sophie Terian with the assistance of ChatGPT and the internet
# 7/30/2024

#User directions:

#First, you need to have arcpy installed and need to set up a virtual environment to use it. Specify the virtual env in the Set Up section. 

#The only things that the user must specify are in the Input and Output section:
#       path to the national watershed polygon dataset (either HUC8, HUC12, etc), 
#       the watershed_id_field that corresponds with the above dataset ^^, i.e. huc12 or huc8, etc
#       path to your nlcd raster, 
#       path to where you want to save your selected watershed shapefile
#       path to where you want to save your watershed land use raster
#       path to where you want to save your csv with land use percentage statistics



############ Set up ###########
import arcpy 
import os 
import csv
arcpy.env.workspace = r"path to your workspace" 
arcpy.env.overwriteOutput = True 



############# Input and output ##########

national_watershed_polygon = r"insert your path here" 
watershed_id_field = "huc12"  # Field that uniquely identifies each watershed in the attribute table 

ncld_raster = r"insert your path here"

specified_watershed_id = "102701010207"  # Replace with the actual ID of the watershed you want to select 

selected_watershed_shapefile = r"insert your path here" 
watershed_landuse_raster = r"insert your path with desired file name.tif"

# Assuming specified watershed ID is a string field 
query = f"{watershed_id_field} = '{specified_watershed_id}'" 
# print(f"Query: {query}")  # Print the query for debugging if needed

statistics_csv = r"insert your path with desired file name.csv"


# Verify if the shapefile exists 
if not arcpy.Exists(national_watershed_polygon): 
    raise FileNotFoundError(f"The input shapefile does not exist: {national_watershed_polygon}") 
  

# Print field names for verification 
fields = [f.name for f in arcpy.ListFields(national_watershed_polygon)] 
print("Fields in the shapefile:", fields) 



  

################# Create a shapefile with the selected watershed ################

selected_layer = "selected_layer" 

try: 

    arcpy.management.MakeFeatureLayer(national_watershed_polygon, selected_layer, query) 
    print(f"Feature layer created successfully with query: {query}") 

except arcpy.ExecuteError as e: 
    print(f"Failed to create feature layer. Error: {e}") 
    arcpy.AddError(e)  # Add error to ArcPy's error log 

  
# Save the selected features to a new shapefile 
try: 
    arcpy.management.CopyFeatures(selected_layer, selected_watershed_shapefile) 
    print(f"Selected features saved to {selected_watershed_shapefile}") 

except arcpy.ExecuteError as e: 
    print(f"Failed to save selected features. Error: {e}") 
    arcpy.AddError(e)  # Add error to ArcPy's error log 







############## Clip the NCLD raster to the selected watershed ###############

#check out spatial analyst 
arcpy.CheckOutExtension("Spatial")

selected_watershed_shapefile = r"C:\Users\s196t023\OneDrive - University of Kansas\Robust Incentives Project\Potential test locations\Minnesota Data arcGIS\MRB_site_watersheds\MRB_site_watersheds.shp"

InRas1 = ncld_raster
InMsk1 = selected_watershed_shapefile

landuse_selected_watershed = arcpy.sa.ExtractByMask(InRas1, InMsk1, "INSIDE")

#save the raster:
landuse_selected_watershed.save(watershed_landuse_raster)

# Release the Spatial Analyst extension
arcpy.CheckInExtension("Spatial")

print(f"Raster saved successfully to {watershed_landuse_raster}")





############ Calculate the percent land use in the watershed ##############

# Define paths
raster_file = watershed_landuse_raster  # Path to the clipped raster

# Initialize dictionary to hold land use value counts
land_use_counts = {}
land_use_names = {}

# Use SearchCursor to read the raster's attribute table
with arcpy.da.SearchCursor(raster_file, ["Value", "Count", "nlcd_land"]) as cursor:
    total_pixels = 0
    for row in cursor:
        value, count, nlcd_land = row
        land_use_counts[value] = count
        land_use_names[value] = nlcd_land
        total_pixels += count

# Calculate percentages
percentages = {value: (count / total_pixels) * 100 for value, count in land_use_counts.items()}

# Export to CSV
with open(statistics_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Land Use Type", "Land Use Name", "Pixel Count", "Percentage"])
    for value, count in land_use_counts.items():
        percentage = percentages[value]
        land_use_name = land_use_names.get(value, "Unknown")
        writer.writerow([value, land_use_name, count, percentage])

print(f"Land use statistics saved to {statistics_csv}")


 

