import pyAGS

from pyAGS import processAGS

fnames = []

fout = "C:\\Users\\thomsonsj\\AECOM\\HS2 North Tender - Documents\\General\\03 Data Analysis\\02 North Table Summary and Kml\\group_lines.csv"
fout2 = "C:\\Users\\thomsonsj\\AECOM\\HS2 North Tender - Documents\\General\\03 Data Analysis\\02 North Table Summary and Kml\\point_group_summary.csv"

folder  = "C:\\Users\\thomsonsj\\AECOM\\HS2 North Tender - Documents\\General\\02 Ground Data\\AGS Files NORTH"

fnames.append (folder + "1G003-ESG-GT-AGS-000-000019 (P03).AGS")
fnames.append (folder + "1G004-IFR-GT-AGS-000-000020 (P02).ags")
fnames.append (folder + "1G006-SEN-GT-AGS-000-000041 (P01).ags")
fnames.append (folder + "1G009-ESG-GT-AGS-000-000023 (P03).AGS")
fnames.append (folder + "1G012-ESG-GT-AGS-000-000016 (P03).AGS")
fnames.append (folder + "1G021-RPS-GT-AGS-000-000013 (P04).ags")
fnames.append (folder + "1G022-RPS-GT-AGS-000-000019 (P05).ags")
fnames.append (folder + "1G023-RPS-GT-AGS-000-000012 (P05).ags")
fnames.append (folder + "1G024-RPS-GT-AGS-000-000012 (P05).ags")
fnames.append (folder + "1G025-FES-GT-AGS-000-000013 (P04).ags")
fnames.append (folder + "1G026-RPS-GT-AGS-000-000025 (P04).ags")
fnames.append (folder + "1G027-ESG-GT-AGS-000-000078 (P04).ags")
fnames.append (folder + "1G027-ESG-GT-AGS-000-000084 (P03).ags")
fnames.append (folder + "1G058-FES-GT-AGS-000-000015 (P05).ags")
fnames.append (folder + "1G105-BAM-GT-AGS-000-000079 (P03).ags")
fnames.append (folder + "1G105-BAM-GT-AGS-000-000085 (P03).ags")
fnames.append (folder + "1G106-SEN-GT-AGS-000-000058 (P04).ags")
fnames.append (folder + "1G106-SEN-GT-AGS-000-000060 (P03).ags")
fnames.append (folder + "1G001-IFR-GT-AGS-000-000018 (P01).ags")
fnames.append (folder + "1G002-IFR-GT-AGS-000-000023 (P01).ags")

ap = processAGS (fnames)
ap.process()
ap.report_lines (fout)
ap.report_summary(fout2)