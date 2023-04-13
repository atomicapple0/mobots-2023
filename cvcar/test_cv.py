from cv import *
import os

src_dir = "imgs/"
dest_dir = "tests/"
jpgs = [jpg for jpg in os.listdir("imgs") if jpg.endswith('jpg')]

for jpg in jpgs:
    src_file = src_dir + jpg
    dest_file = dest_dir + jpg
    