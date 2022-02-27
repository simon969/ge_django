import pyAGS

from pyAGS import processAGS


fnames = []
folder = "C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\\R19\\"
fout = "group_lines.csv"
fout2 = "group_point_summary.csv"

fnames.append (folder + "MONAGS-X-X-R19-X-X-X.X-X.X-0001 1 of 1.ags")
fnames.append (folder + "MONAGS-SU-X-R19-X-X-X.X-X.X-0001.ags")

ap = processAGS (fnames)
ap.process()
ap.report_lines (folder + fout)
ap.report_summary (folder + fout2)
