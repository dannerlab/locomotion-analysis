""" after splitting smr files, run this first to convert to h5 """

import os

def batch_convert(groups, data_folder):

    dirs = []
    for group in groups:
        directory = f'{data_folder}/{group}/smr'
        dirs.append(directory)

    convert_to_h5 = "Scripts/convert_to_h5.py"

    processed_files = 0

    for directory in dirs:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                f = os.path.join(directory, file)
                os.system(f'python {convert_to_h5} -f {f} -u')   #runs convert_to_h5.py with u units on the files in the directory
                processed_files += 1

        else:
            print(directory)
            print("the file path you entered does not exist\n")

    print(f'processed files: {processed_files}')

def main():
    groups = ["V3Off_Levelwalk", "WT_Levelwalk"]
    data_folder = "Full_data" #"Sample_data"
    batch_convert(groups, data_folder)

if __name__ == "__main__":
    main()