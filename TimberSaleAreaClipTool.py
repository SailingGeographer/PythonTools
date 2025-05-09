import arcpy
import os
import re
from openpyxl import Workbook

def sanitize_name(value):
    return re.sub(r"[^a-zA-Z0-9_]", "_", str(value))[:50]

def main():
    input_fc_workspace = arcpy.GetParameterAsText(0)
    timber_sale_fc = arcpy.GetParameterAsText(1)
    output_workspace = arcpy.GetParameterAsText(2)
    output_log_xlsx = arcpy.GetParameterAsText(3)
    match_field = "sale_name"

    arcpy.env.workspace = input_fc_workspace
    arcpy.env.overwriteOutput = True

    if not arcpy.Exists(output_workspace) or not output_workspace.endswith(".gdb"):
        arcpy.AddError("Output workspace must exist and be a File Geodatabase (.gdb)")
        return

    input_feature_classes = arcpy.ListFeatureClasses()
    if not input_feature_classes:
        arcpy.AddError("No input feature classes found.")
        return

    sale_ids = {row[0] for row in arcpy.da.SearchCursor(timber_sale_fc, [match_field]) if row[0] is not None}
    log_entries = []

    for sale_id in sale_ids:
        safe_id = sanitize_name(sale_id)
        query_value = str(sale_id).replace("'", "''")
        sale_query = f"{arcpy.AddFieldDelimiters('', match_field)} = '{query_value}'"
        arcpy.MakeFeatureLayer_management(timber_sale_fc, "sale_layer", sale_query)

        if int(arcpy.GetCount_management("sale_layer")[0]) == 0:
            arcpy.AddWarning(f"No polygons found for Sale Name: {sale_id}")
            continue

        group_path = os.path.join(output_workspace, f"Sale_{safe_id}")
        if not arcpy.Exists(group_path):
            arcpy.CreateFeatureDataset_management(output_workspace, f"Sale_{safe_id}", arcpy.Describe(timber_sale_fc).spatialReference)

        for input_fc in input_feature_classes:
            input_fc_path = os.path.join(input_fc_workspace, input_fc)
            arcpy.MakeFeatureLayer_management(input_fc_path, "input_layer")

            arcpy.SelectLayerByLocation_management("input_layer", "INTERSECT", "sale_layer")

            if int(arcpy.GetCount_management("input_layer")[0]) == 0:
                arcpy.AddWarning(f"No intersecting features in {input_fc} for {sale_id}")
                continue

            out_name = f"{os.path.splitext(input_fc)[0]}_{safe_id}_clip".replace(" ", "_")
            out_path = os.path.join(group_path, out_name)

            arcpy.Clip_analysis("input_layer", "sale_layer", out_path)

            if match_field not in [f.name for f in arcpy.ListFields(out_path)]:
                arcpy.AddField_management(out_path, match_field, "TEXT")

            with arcpy.da.UpdateCursor(out_path, [match_field]) as cursor:
                for row in cursor:
                    row[0] = sale_id
                    cursor.updateRow(row)

            log_entries.append([out_path, sale_id])
            arcpy.AddMessage(f"Clipped {input_fc} to {sale_id} -> {out_path}")

    if log_entries:
        wb = Workbook()
        ws = wb.active
        ws.title = "Clip Log"
        ws.append(["OutputFeatureClassPath", match_field])
        for entry in log_entries:
            ws.append(entry)
        wb.save(output_log_xlsx)
        arcpy.AddMessage(f"Excel log written to {output_log_xlsx}")
        try:
            os.startfile(output_log_xlsx)
        except Exception as e:
            arcpy.AddWarning(f"Could not open Excel file: {e}")
    else:
        arcpy.AddWarning("No clips performed. No Excel log created.")

    arcpy.AddMessage("All processing completed.")

if __name__ == "__main__":
    main()
