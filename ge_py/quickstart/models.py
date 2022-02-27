import os
from typing import Any
from django.db import models

# Create your models here.


def split_trim(s):
    if "," in s:
        ary = [x.strip() for x in s.split(',')]
        return ary
    ary =  s.split();
    return ary

def index_match(s_array, s_match, match_case, not_found):
        offset = int() 
        for s in s_array:
            if match_case  and s == s_match:
                return offset 
            if not match_case and s.lower()== s_match.lower():
                return offset
            offset += 1
        return int(not_found)

def file_name(s):
 return os.path.basename(s)

NOT_INTEGER  = -1

def get_integer (n, not_integer=NOT_INTEGER):
    try:
        n_int = int(n)
        return n_int
    except ValueError:
        return not_integer

def is_integer_num(n):
    try:
        # if isinstance(n, int):
        #     return True
        # if isinstance(n, float):
        #     return n.is_integer()
        n_int = int(n)
        return True
    except ValueError:
        return False
def is_null_or_empty(s):
    try:
        if len(s)==0:
            return True
        else:
            return False  
    except:
        return True 

