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

3_AGOLSendAccountDeleteEmail.ipynb

This repository includes an ArcGIS Notebook designed to automate email notifications for AGOL account deletions. By inputting a list of users marked for deletion, the notebook generates and sends templated emails notifying users of their account status, ensuring clear communication and compliance with organizational policies.

The notebook integrates the ArcGIS API for Python to manage user accounts and uses Python's built-in email libraries (or third-party tools if configured) to send notifications. Clear markdown and input prompts guide the user through uploading the list of accounts, customizing email templates, and executing the notification process.

This tool is ideal for GIS admins needing an efficient, repeatable way to handle account closures while keeping stakeholders informed.

Author: Jeff Erwin Contact: See profile for further details.

ExcelCombineExcelFilesToOne.ipynb

This repository provides an ArcGIS Notebook (or standalone Python notebook) that automates the process of combining multiple Excel files into a single workbook, with each original file placed into its own sheet. This is useful for consolidating datasets from multiple sources or standardizing data intake workflows.

The notebook uses pandas and openpyxl to read Excel files from a specified directory and write them into a unified Excel workbook. Users are prompted to provide the source folder path and output filename. The notebook also includes basic error handling and markdown instructions to make the process straightforward.

This tool is perfect for data analysts or GIS professionals who manage multiple Excel datasets and need a fast, reliable way to merge them into one file for reporting or further analysis.

Author: Jeff Erwin Contact: See profile for details.

ExcelSplitByColumn.ipynb

This repository contains a Python notebook that splits a single Excel file into multiple workbooks based on the unique values of a specified column. Each resulting Excel file contains only the rows corresponding to one unique value, making it easy to segment data for distribution, reporting, or analysis.

The notebook uses pandas and openpyxl to process the Excel file. Users are prompted to input the path to the source Excel file, the column to split by, and the output folder path. Clear markdown sections and prompts walk the user through setup, execution, and output review.

This tool is ideal for data analysts or GIS professionals who need to distribute data subsets to different stakeholders or organize large datasets quickly and efficiently.

Author: Jeff Erwin Contact: See profile for more information.

SendAGOLNotification.ipynb

This repository provides an ArcGIS Notebook designed to send custom notifications to ArcGIS Online (AGOL) users or groups. The notebook allows admins to craft and dispatch messages programmatically, streamlining communication for updates, maintenance notices, or other announcements.

Built using the ArcGIS API for Python, the notebook prompts the user to input recipient details, message content, and delivery options. It is equipped with clear markdown sections, step-by-step prompts, and guidance to ensure smooth operation even for those new to scripting notifications.

This tool is ideal for GIS administrators needing an efficient way to communicate with AGOL users directly through the platform’s messaging system.

Author: Jeff Erwin Contact: See profile for details.

TimberSlaeAreaClipTool.py

This repository contains a Python script designed for use as an ArcGIS Pro script tool that clips multiple feature classes based on polygon boundaries for timber sale areas. The tool processes all feature classes within a specified workspace, clipping them to match each timber sale polygon, grouping outputs by sale ID, and logging results to an Excel spreadsheet.

Key features include:

Dynamically lists and processes all input feature classes.

Clips intersecting features to timber sale polygons.

Creates organized output datasets within a geodatabase, grouped by sale ID.

Adds a sale_name field to clipped outputs to maintain traceability.

Logs output paths and sale IDs to an Excel workbook, and attempts to open it upon completion.

Ideal for forestry GIS teams managing large datasets across multiple sales, the script improves workflow efficiency and ensures output traceability.

Author: Jeff Erwin Contact: See profile for details.

ProjectClipReprojectTool_ArcGIS_PRO.pyt

This repository contains a custom Python toolbox (.pyt) for ArcGIS Pro designed to streamline the process of clipping and reprojecting geospatial datasets to match the extent and projection of Region 9 forestry projects. The tool allows users to select input data, define the target extent and projection, and output consistent, project-ready datasets in a single automated workflow.

Key features:

Clips input data to a user-specified project boundary.

Reprojects clipped data to a target coordinate system.

User-friendly parameters for input paths, projection selection, and output destinations.

Built to support forestry and environmental planning teams in maintaining clean, standardized datasets.

This toolbox is ideal for GIS specialists working on USFS Region 9 projects who need to prepare spatial data efficiently and consistently across multiple projects.

Author: Jeff Erwin Contact: See profile for more details.

DataCompareSUIDsV2.ipynb

This repository includes an ArcGIS Notebook designed to compare two datasets by their unique identifiers (SUIDs) and identify discrepancies between them. The notebook reads two input datasets, compares based on a specified SUID field, and outputs a report highlighting records that are missing, mismatched, or duplicated.

Key features:

Prompts for input file paths and SUID field selection.

Performs side-by-side comparisons to quickly identify inconsistencies.

Outputs results to Excel or CSV for easy review and follow-up.

Designed with clear markdown instructions and modular code for customization.

Ideal for data stewards and GIS analysts performing QA/QC tasks on spatial or tabular datasets where SUID consistency is critical.

Author: Jeff Erwin Contact: See profile for details.

BCSBuffering.py
# BCS Hibernacula Location Buffering Script

## Overview

This ArcGIS Pro Python script generates buffer polygons for bat habitat locations (hibernacula, roosts, and maternity capture points) in support of the **Bat Conservation Strategy (BCS)**. It processes site and observation data exported from the USFS Geospatial Interface (GI) Visualization workflow and creates spatial buffers following BCS biological rules and thresholds.

### Author(s)

- Philip Marley  
- Jeffery Erwin  
- Walker Johnson

### Maintainer Contact

- jeffery.erwin@usda.gov  
- philip.marley@usda.gov  
- george.w.johnson@usda.gov

---

## Features

- Calculates visit sequence to identify most recent data.
- Determines historic vs. active site status.
- Evaluates bat species abundance and determines pre/post White-Nose Syndrome (WNS) exposure.
- Generates individual point records and buffers based on biological thresholds for:
  - **Hibernacula Sites**
  - **Roost Sites (including maternity roosts and active snags)**
  - **Maternity Capture Locations**

- Outputs a final buffer polygon feature class suitable for web mapping or analysis.

---

## Input Requirements

This tool must be run within **ArcGIS Pro** as a script tool, and requires:

1. **Site/Observation Layer**: Exported from the GI tool.
2. **Capture Layer**: Capture data from GI workflow.
3. **Output Workspace**: File geodatabase where output buffers will be stored.

---

## Species Codes

- `MYSO`: Indiana Bat (*Myotis sodalis*)
- `MYSE`: Northern Long-eared Bat (*Myotis septentrionalis*)
- `MYLU`: Little Brown Bat (*Myotis lucifugus*)
- `PESU`: Tri-colored Bat (*Perimyotis subflavus*) or (*Pipistrellus subflavus*)
- `Chiroptera`: All bats

---

## Buffering Rules (Examples)

### Hibernacula Buffers (MYSO/MYLU Combined Abundance)
| Abundance | Primary | Secondary | Tertiary |
|----------|---------|-----------|----------|
| High (≥ 5000) | 500 ft | 2 mi | 5 mi |
| Moderate (20–4999) | 500 ft | 2 mi | — |
| Low (1–19) | 500 ft | — | — |

### Roost Buffers
| Species | Primary | Maternity |
|---------|---------|-----------|
| Indiana/Little Brown | 150 ft | 1.8 mi |
| Northern Long-eared | 150 ft | 0.25 mi |
| Tricolored | 150 ft | 300 ft |

---

## Output

- `ptBufferFC`: Point feature class with attributes defining site ID, species, buffer type, and distance.
- `BCSBuffers_<date>`: Final polygon feature class with applied buffer distances.

---

## Dependencies

- ArcGIS Pro (with arcpy)
- pandas
- Python 3.x

This script uses the ArcPy site package provided with ArcGIS Pro and is not compatible with standalone Python environments.

---

## How to Run

1. Load `BCSBuffering.py` into an ArcGIS Pro toolbox as a script tool.
2. Provide the required input layers and workspace.
3. Run the tool — outputs are added to the map automatically.

---

## License

This script is intended for use within USFS or its partners in bat conservation efforts. Not licensed for commercial distribution.

---

## Version History

- **v0.0.1** – Initial development version

---

## Acknowledgments

This tool supports the USFS Bat Conservation Strategy by automating complex GIS buffering workflows aligned with biological standards. Contributions by R9 Information Management and Bat Conservation teams.







