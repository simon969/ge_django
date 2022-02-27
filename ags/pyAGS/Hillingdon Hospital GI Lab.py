import pyAGS

from pyAGS import processAGS

fnames = []

folder  = "C:\\Users\\thomsonsj\\AECOM\\Hillingdon Hospital GI - Documents\\General\\16 Draft Factual Report\\2022-01-11 Lab Results\\INTERIM 23122021 Check\\"

fnames.append (folder + "D1043-21-23122021.ags")
fnames.append (folder + "21-26216_DETS_16122021_V4.AGS")
fnames.append (folder + "21-24889_DETS_29112021_V4.AGS")
fnames.append (folder + "21-25178_DETS_01122021_V4.AGS")
fnames.append (folder + "21-25179_DETS_01122021_V4.AGS")

ap = processAGS (fnames)
ap.process()
ap.report_lines (folder + "group_lines.csv")
ap.report_summary(folder + "point_group_summary.csv")