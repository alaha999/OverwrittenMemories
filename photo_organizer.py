import os,sys
import random

folder = sys.argv[1]
filelist = os.listdir(folder)
#print(filelist)

filelist = random.sample(filelist,len(filelist))

for index,item in enumerate(filelist):
    
    file_ext = item.split(".")[1]
    newname = f"Photo_{index+1:02d}.{file_ext}"
    print(f"{item} --> {newname}")
    cmd = f"mv {folder}/{item} {folder}/{newname}"
    print(cmd)
    os.system(cmd)
    
