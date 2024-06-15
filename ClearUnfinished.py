import os
import shutil
# clear which were not finished for some reasone (no Finished.txt file)

indir="/mnt/306deddd-38b0-4adc-b1ea-dcd5efc989f3/python_project/TextutreExtracture/2D_MateSeg/"
unfinished_dir ="/mnt/306deddd-38b0-4adc-b1ea-dcd5efc989f3/python_project/TextutreExtracture/unfinished/"
if not os.path.exists(unfinished_dir):os.mkdir(unfinished_dir)
for sdr in os.listdir(indir):
    if not os.path.exists(indir+"/"+sdr+"/Finished.txt"):
         shutil.move(indir+"/"+sdr,unfinished_dir+"/"+sdr)
         print("Moved ",indir+"/"+sdr,unfinished_dir+"/"+sdr)
print("Finished")