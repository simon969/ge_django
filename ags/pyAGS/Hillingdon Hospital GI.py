import pyAGS

from pyAGS import processAGS

fnames = []

folder  = "C:\\Users\\thomsonsj\\AECOM\\Hillingdon Hospital GI - Documents\\General\\16 Draft Factual Report\\D1043-21 Interim Draft Check\\"

fnames.append (folder + "D1043-21 Interim Draft AGS.AGS")


ap = processAGS (fnames)
ap.process()
ap.report_lines (folder + "group_lines.csv")
ap.report_summary(folder + "point_group_summary.csv")