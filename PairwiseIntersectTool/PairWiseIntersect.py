'''
PairWiseIntersect.py
Perform pair wise intersect using geometry Intersect method and
transfers Attributes from both inputs.

Usage:
PairWiseIntersect.py <Input Features> <Intersecting Features> <Output Featureclass> <Input Feature Fields to transfer to output>

<Input Features> - The features to iterate over, one by one and intersect with the features in <Intersecting Features>.
<Intersecting Features> - The features <Input Features> are intersected with.
<Output Featureclass> - The output featureclass.
<Input Feature Fields to transfer to output> - List of fields from <Input Features> to transfer to the <Output Featureclass>

Ken Hartling
ESRI
380 New York St.
Redlands, CA, USA 92373
909-793-2853
'''
import os
import time
import arcpy

arcpy.env.workspace = os.getcwd()
arcpy.env.overwriteOutput = True
arcpy.env.addOutputsToMap = False

def pairWiseIntersect(inputFC1, inputFC2, outputFC, fldList2Transfer):
    """
    Intersect each feature in layer1 with the features it overlaps in layer2.
    """
    # Prep for processing
    # Determine if the inputs are layers or featureclass
    if arcpy.Describe(inputFC1).datasetType == "FeatureClass":
        inputLayer1 = arcpy.MakeFeatureLayer_management(inputFC1,"inputLayer1")
    else:
        inputLayer1 = inputFC1

    if arcpy.Describe(inputFC2).datasetType == "FeatureClass":
        inputLayer2 = arcpy.MakeFeatureLayer_management(inputFC2,"inputLayer2")
    else:
        inputLayer2 = inputFC2

    # Get the input geometry type for use in the geometry intersect method
    layer1Type = arcpy.Describe(inputLayer1).shapeType
    layer2Type = arcpy.Describe(inputLayer2).shapeType
    if layer1Type == "Point" or layer2Type == "Point":
        dimension = 1
    elif layer1Type == "Polyline" or layer2Type == "Polyline":
        dimension = 2
    else:
        dimension = 4

    arcpy.AddMessage(time.ctime())
    startProcessing = time.time()

    # Setup input fields
    tempFldsInput1 = [f.name.upper() for f in arcpy.ListFields(inputLayer1)]
    fldsInput1 = list(tempFldsInput1)
    fldsInput1.remove(arcpy.Describe(inputLayer1).shapeFieldName.upper())
    fldsInput1.remove(arcpy.Describe(inputLayer1).oidFieldName.upper())
    fldsInput1.append("shape@")

    fldsInput2Orig = arcpy.ListFields(inputLayer2)
    fldsInput2 = fldList2Transfer.upper().split(";")
    try:
        fldsInput2.remove("") #Take care of case where no fields were selected
    except Exception:
        pass
    try:
        fldsInput2.remove(arcpy.Describe(inputLayer2).shapeFieldName.upper())
    except Exception:
        pass # Shapefile was not in the input list
    try:
        fldsInput2.remove(arcpy.Describe(inputLayer2).oidFieldName.upper())
    except Exception:
        pass # OID was not in the input list
    fldsInput2.append("shape@")

    # Setup the output feature class for receiving spatial data from the intersect operation
    # and attribute data from both the inputs.
    arcpy.CreateFeatureclass_management(os.path.dirname(outputFC),
                                        os.path.basename(outputFC),
                                        layer1Type,
                                        inputLayer1,
                                        spatial_reference=inputLayer1)
    arcpy.MakeFeatureLayer_management(outputFC, r"outputLayer")
    
    fldsInput2Modified = []
    for fld in fldsInput2:
        if fld == "shape@":
            pass
        else:
            for fldOrig in fldsInput2Orig:
                if fldOrig.name.upper() == fld:
                    if fld in fldsInput1:
                        newFld = fld + "_1"
                        fldsInput2Modified.append(newFld)
                    else:
                        newFld = fld
                    arcpy.AddField_management(r"outputLayer", newFld, fldOrig.type)
                    break

    tempFldsOutput = [f.name.upper() for f in arcpy.ListFields(r"outputLayer")]
    fldsOutput = list(tempFldsOutput)
    fldsOutput.remove(arcpy.Describe(r"outputLayer").shapeFieldName.upper())
    fldsOutput.remove(arcpy.Describe(r"outputLayer").oidFieldName.upper())
    fldsOutput.append("shape@")

    # Make sure to only process features in input1 that intersect something in input2.
    arcpy.SelectLayerByLocation_management(inputLayer1, "INTERSECT", inputLayer2)

    # Intersect each input feature with the features from the second input feature class and
    # determine the field values to be transfered to the output
    arcpy.AddMessage("Processing features...")
    inCursor = arcpy.da.InsertCursor(r"outputLayer", fldsOutput)
    with arcpy.da.SearchCursor(inputLayer1, fldsInput1) as cursor:
        for cnter, row in enumerate(cursor, 1):
            if cnter%250 == 0:
                arcpy.AddMessage("{} Features processed... ".format(str(cnter)))
            arcpy.SelectLayerByLocation_management(inputLayer2, "INTERSECT", row[-1])
            with arcpy.da.SearchCursor(inputLayer2, fldsInput2) as cursor2:
                for row2 in cursor2:
                    clippedFeature = row2[-1].intersect(row[-1], dimension)
                    # Determine the field values to insert in the output
                    flds2Insert = list(fldsOutput)
                    for i, outFlds in enumerate(fldsOutput):
                        found = False
                        # Process the first layers attribute values
                        for j, input1Fld in enumerate(fldsInput1):
                            if input1Fld != "shape@" and outFlds != "shape@":
                                if outFlds == input1Fld:
                                    flds2Insert[i] = row[j]
                                    found = True
                                    break
                        # Process the second layers attribute values
                        if found == False:
                            for f, fldIn2 in enumerate(fldsInput2):
                                if fldIn2 != "shape@" and outFlds != "shape@":
                                    if outFlds in fldsInput2 or outFlds in fldsInput2Modified:
                                        if fldIn2 == outFlds or fldIn2 + "_1" == outFlds:
                                            flds2Insert[i] = row2[f]
                                            break
                                    else:
                                        break
                                else:
                                    break
                    flds2Insert[-1] = clippedFeature
                    inCursor.insertRow(flds2Insert)
    try:
        del inCursor
        del cursor, cursor2
    except:
        pass
    
    stopProcessing = time.time()
    if False: # set to true if running as a stand alone script
        arcpy.AddMessage("Time to process data = {} seconds; in minutes = {}".format(str(int(stopProcessing-startProcessing)), str(int((stopProcessing-startProcessing)/60))))
        arcpy.AddMessage("*****DONE*****")
    
if __name__ == '__main__':
    inputFC1 = arcpy.GetParameterAsText(0)
    inputFC2 = arcpy.GetParameterAsText(1)
    outputFC = arcpy.GetParameterAsText(2)
    fldList2Transfer = arcpy.GetParameterAsText(3)
    pairWiseIntersect(inputFC1, inputFC2, outputFC, fldList2Transfer)