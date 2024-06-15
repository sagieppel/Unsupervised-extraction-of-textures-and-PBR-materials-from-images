while true
do
   echo "Running blender"
   blender DatasetGeneration.blend --background -noaudio -P  main.py 
   echo "-------------Finished Or Crushed-------------"
done


