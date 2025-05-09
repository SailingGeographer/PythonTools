# PythonTools
Python tools and scripts I have created or collaborated on in the past. Most are in the form of ArcGIS Notebooks which I favor when working with spatial data.

1_AGOLGroupmembers.ipynb

This repository contains an ArcGIS Notebook designed to export ArcGIS Online (AGOL) group member details into an Excel file. The notebook allows you to input a Group ID and extract a full list of group members, including their Eauth Number, Full Name, Role, Email, and Last Login. This tool is ideal for GIS administrators and analysts who need to audit group membership or create reports for compliance and tracking purposes.

The notebook connects to AGOL using the ArcGIS API for Python, retrieves group member data, formats it into a pandas DataFrame, and outputs a well-structured Excel file. It’s lightweight, user-friendly, and includes clear markdown sections and prompts to guide users through login, data extraction, and export.

Please refer to the notebook for detailed instructions on setup, required inputs, and sample outputs. Ensure you have appropriate AGOL permissions to access group data.

Author: Jeff Erwin Contact: See profile for more information.

2_AGOLGroupContent.ipynb

This repository contains an ArcGIS Notebook that extracts and exports content details from an ArcGIS Online (AGOL) group. By specifying a Group ID, the notebook retrieves a full inventory of the group's hosted items, including titles, item types, owners, creation dates, and last modified dates. The results are exported to an Excel file for easy auditing and record-keeping.

This tool is valuable for GIS administrators and analysts who manage AGOL groups and need insight into content distribution, ownership, and update frequency. The notebook uses the ArcGIS API for Python, pandas for data handling, and includes clear markdown and prompts to walk users through the workflow.

Please consult the notebook for setup steps, required inputs, and output examples. Ensure you have sufficient AGOL permissions to access group content.

Author: Jeff Erwin Contact: See profile for more details.
