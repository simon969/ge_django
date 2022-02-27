import pyAGS

from pyAGS import processAGS


fnames = []
folder = "C:\\Users\\thomsonsj\\AECOM\\LTC P3 Long Term Monitoring - General\\10_Deliverables\\01 Data processing\\06 LRMONGW\\R19\\Uploaded to gINT database\\"
fout = "group_lines.csv"
fout2 = "group_point_summary.csv"

fnames.append (folder + "LRGWMON R19.ags")

ap = processAGS (fnames)
ap.process()
ap.report_lines (folder + fout)
ap.report_summary (folder + fout2)
