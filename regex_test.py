import re


line = "<Idle|WPos:69.000,40.000,-20.000|Bf:15,128|FS:0,0>"
pattern = r"<[^|]*\|WPos:([^,]*),([^,]*),([^|]*)\|"
m = re.match(pattern, line)

if m:
    print("Group 1 (X):", m.group(1))
    print("Group 2 (Y):", m.group(2))
    print("Group 3 (Z):", m.group(3))
else:
    print("No match found.")