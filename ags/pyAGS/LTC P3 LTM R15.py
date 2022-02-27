import pyAGS

from pyAGS import processAGS


fnames = []

fout = "C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002_.csv"
fout2 = "C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002_ByPOINT.csv"

fnames.append ("C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 1 of 12.ags")
fnames.append ("C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 2 of 12.ags")
fnames.append ("C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 3 of 12.ags")
fnames.append ("C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 4 of 12.ags")
fnames.append ("C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 5 of 12.ags")
fnames.append ( "C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 6 of 12.ags")
fnames.append ("C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 7 of 12.ags")
fnames.append ( "C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 8 of 12.ags")
fnames.append ("C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 9 of 12.ags")
fnames.append ( "C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 10 of 12.ags")
fnames.append ("C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 11 of 12.ags")
fnames.append ( "C:\\Users\\thomsonsj\\AECOM\\LTC AGS Checking - LTM Phase 3 AGS Processing\\05 AGS\\10 QAQC\R15\P02\MONAGS-X-X-R15-X-X-X.X-X.X-0002 12 of 12.ags")

ap = processAGS (fnames)

ap.report_lines (fout)
ap.report_summary(fout2)
