import pyAGS

from pyAGS import processAGS

fnames = []

fout = "C:\\Users\\thomsonsj\\AECOM\\HS2 North Tender - Documents\\General\\03 Data Analysis\\04 Urban Table Summary and Kml\\group_lines.csv"
fout2 = "C:\\Users\\thomsonsj\\AECOM\\HS2 North Tender - Documents\\General\\03 Data Analysis\\04 Urban Table Summary and Kml\\point_group_summary.csv"

folder  = "C:\\Users\\thomsonsj\\AECOM\HS2 North Tender - Documents\\General\\02 Ground Data\AGS Files URBAN\\"

fnames.append (folder + "1G087-SEN-GT-AGS-000-000072 (P03).ags")
fnames.append (folder + "1G088-WYG-GT-AGS-000-000042 (P05).ags")
fnames.append (folder + "1G089-FES-GT-AGS-000-000099 (P04).ags")
fnames.append (folder + "1G101-FES-GT-AGS-000-000089 (P03).ags")
fnames.append (folder + "1G101-FES-GT-AGS-000-000093 (P03).ags")
fnames.append (folder + "1G107-FES-GT-AGS-000-000198 (P04).ags")
fnames.append (folder + "1G080-FES-GT-AGS-000-000052 (P03).ags")
fnames.append (folder + "1G081-WYG-GT-AGS-000-000017 (P05).ags")
fnames.append (folder + "1G084-RPS-GT-AGS-000-000016 (P01).ags")

ap = processAGS (fnames)
ap.process()
ap.report_lines (fout)
ap.report_summary(fout2)