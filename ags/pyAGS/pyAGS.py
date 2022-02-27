import os

class ags_group:
    def __init__(self, group, line_start):
        self.group = group
        self.line_start = line_start
        self.headings = [] 
        self.units = []
        self.types = [] 
        self.data = []
    def line_end (self, line_end):
        self.line_end = line_end
    def split_headings(self):
        g = self.clean_split(self.group)
        self.name = g[1]
        self.headings = self.clean_split(self.heading)
        self.units = self.clean_split(self.unit)
        self.types = self.clean_split(self.type)

    def clean_split (self, s):
        s = s.replace("\"","") 
        s = s.replace("\n","")
        return s.split(",")

class result:
    def __init__(self, file, group, line_start, line_end):
        self.file = file
        self.group = group
        self.line_start = line_start
        self.line_end = line_end
    def as_csv(self):
        return self.file + ',' + self.group + ',' + str(self.line_start) + ',' + str(self.line_end)
class result_bypoints:
    def __init__(self, file, group, point, count):
        self.file = file
        self.group = group
        self.point = point
        self.count = count
    def as_csv(self):
        return self.file + ',' + self.group + ',' + str(self.point) + ',' + str(self.count)
class group_summary:
    def __init__(self, ags_group):
        self.ags_group = ags_group
        self.points = {}
    def by_point(self):
        point_col = None
        for i, x in enumerate(self.ags_group.headings):
            if (x == "LOCA_ID"):
                point_col = i
        if point_col is not None:
            for s in self.ags_group.data:
                d = self.ags_group.clean_split(s)
                point = d[point_col]
                exist_count = self.points.get(point)
                if (exist_count is None):
                    self.points[point] = 1
                else:
                    update = {point: exist_count +1 } 
                    self.points.update (update)
        return self.points
    def by_result(self, filename):
            self.by_point()
            results = [] 
            for i, (point, count) in enumerate(self.points.items()):
                result = result_bypoints(filename, self.ags_group.name, point, count)
                results.append(result)
            return results



class processAGS:
    def __init__(self, fnames):
        self.fnames = fnames
        self.results =[]
        self.results_bypoints = []

    def process(self):
        for fname in self.fnames:
            print("Processing:" + fname)
            with open(fname) as file_in:
                lines = []
                ags_groups = []
                count = 0
                fname2 = os.path.basename(fname)
                g = None
                for line in file_in:
                    if "\"GROUP\"," in line[0:12]:
                        g =  ags_group (line, count)   
                    if "\"UNIT\"," in line[0:7]:
                        g.unit = line
                    if "\"HEADING\"," in line[0:10]:
                        g.heading = line
                    if "\"TYPE\"," in line[0:7]:
                        g.type = line
                    if "\"DATA\"," in line[0:7]:
                        g.data.append(line)    
                    if line == '\n' and g is not None:
                        g.line_end = count - 1    
                        ags_groups.append (g)
                        g = None
                    lines.append(line)
                    count = count + 1
                if ags_groups is not None:
                    for g in ags_groups:
                        name = g.group.split(",")
                        r1 = result (fname2,name[1].strip(),g.line_start,g.line_end)
                        self.results.append (r1)
                        g.split_headings()
                        sg = group_summary(g)
                        rps = sg.by_result(fname2)
                        for rp in rps:
                            self.results_bypoints.append(rp)  
        
    def report_lines(self, fout=None):
            header = 'file_name,group_name,line_start,line_end\n'
            rows = ""
            if fout is not None:
                with open(fout, "w") as file_out:
                    file_out.write(header) 
                    for r in self.results:
                        file_out.write (r.as_csv() + '\n')
                return
            
            for r in self.results:
                rows += r.as_csv() + '\n'
            return header+rows

    def report_summary(self, fout=None):
            header = 'file_name,group_name,pointid,count\n'
            rows = ""
            if fout is not None:
                with open(fout, "w") as file_out:
                    file_out.write(header) 
                    for r in self.results_bypoints:
                        file_out.write (r.as_csv() + '\n')
                return
            for r in self.results_bypoints:
                rows += r.as_csv() + '\n'
            return header+rows