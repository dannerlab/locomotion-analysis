#after splitting files, run this first to convert from smr to h5
#run from GitHub directory containing both locoproc & mouse-V3-analysis
#afterwards, it is recommended to manually move h5 files to an h5 only directory
#should also move the phase files to the phase file directory

import os

#directory = input("Enter the file path of the folder containing smr files you want to convert to h5: ")
directory = 'mouse-V3-analysis/data/kinematics-modeling-v1/MUT_incline/smr'
print(f'filepath: {directory}' )
total_files = len(os.listdir(directory))
exists = os.path.exists(directory)

convert_to_h5 = "locoproc/script/convert_to_h5.py"

processed_files = 0
if os.path.exists(directory):
    for file in os.listdir(directory):
        f = os.path.join(directory, file)
        os.system(f'python {convert_to_h5} -f {f} -u')   #runs convert_to_h5.py with u units on the files in the directory
        processed_files += 1

else:
    print("the file path you entered does not exist")

print(f'processed files: {processed_files}/{total_files}')