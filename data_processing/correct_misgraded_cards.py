#!/usr/bin/env python3
import pandas as pd
import os
pd.set_option('display.max_columns', 15)
pd.set_option("display.max_colwidth", None)  # after this you can print any column length
pd.set_option('display.width', 5000)

## This script was written to keep track of all of the cards that were incorrectly labeled with their grade,
# a lot of the cards, are PSA 10, eventhough in their ebay listing and on collectors.com they are listed as 
# PSA 1. 
# > grade changes were determined by manually checking
# > these are the card numbers that need to be either deleted or moved into the other folders

## Define the images that need to have their graded changed
grade_corrections_dict = {
    "one_to_ten" : "1,4,10,11,18,24,40,56,58,73,74,77,82,91,92,102,104,109,112,116,122,132,136,143,169,173,180,190,194,200,222,224,241,245,256,269,283,287,290,291,292,297,298,304,310,313,316,324,326,334,335,340,344,350,355,357,366,373,379,382,383,414,423,430,437,439,444,477,482,489,499,500,506,510,512,515,518,524,527,530,531,533,544,547,552,560,563,569,579,590,601,606,607,612,637,653,660,661,674,677,678,685,690,702,703,715,721,726,735,736,740,744,750,754,766,772,785,788,799,806,808,812,824,830,831,834,844,857,862,869,875,879,883,887,888,890,892,898,904,905,918,924,927,934,937,938,940,942,949,954,957,962,972,991,994".split(','),
    "ten_to_one" : "10,11,16,158,169,173,210,290,321,419,463,470,477".split(','),
    "one_to_two" : "990".split(','),
    "one_to_nine" : "179".split(','),
    "ten_to_eight" : "483".split(','),
    "ten_to_nine" : "185".split(',')
}

# make the oldGrade and newGrade columns
old_grades, new_grades = [], []
old_grades.extend([1]*len(grade_corrections_dict["one_to_ten"]))
old_grades.extend([10]*len(grade_corrections_dict["ten_to_one"]))
old_grades.extend([1]*len(grade_corrections_dict["one_to_two"]))
old_grades.extend([1]*len(grade_corrections_dict["one_to_nine"]))
old_grades.extend([10]*len(grade_corrections_dict["ten_to_eight"]))
old_grades.extend([10]*len(grade_corrections_dict["ten_to_nine"]))
new_grades.extend([10]*len(grade_corrections_dict["one_to_ten"]))
new_grades.extend([1]*len(grade_corrections_dict["ten_to_one"]))
new_grades.extend([2]*len(grade_corrections_dict["one_to_two"]))
new_grades.extend([9]*len(grade_corrections_dict["one_to_nine"]))
new_grades.extend([8]*len(grade_corrections_dict["ten_to_eight"]))
new_grades.extend([9]*len(grade_corrections_dict["ten_to_nine"]))

# make the columns of card numbers
card_number = []
for k, v in grade_corrections_dict.items():
    card_number.extend(v)

# define the pandas df with all of this information
grade_corrections_dict = pd.DataFrame(
    {'oldGrade': list(map(int,old_grades)),
     'newGrade': list(map(int,new_grades)),
     'cardNum': card_number
    })

# construct the filename, and the full path for where the file is
grade_corrections_dict['oldFileName'] = grade_corrections_dict.apply(lambda row: "card{}_PSA{}.jpg".format(row.cardNum, row.oldGrade), axis=1)
grade_corrections_dict['filePath'] = grade_corrections_dict.apply(lambda row: "/Users/brianmiller/Desktop/trading_card_data/verified_data/psa{}/{}".format(row.oldGrade, row.oldFileName), axis=1)


# Delete files
for file_path in grade_corrections_dict['filePath'].to_list():
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(f"File not found: {file_path}")
