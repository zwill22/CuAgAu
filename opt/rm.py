import os

folder = "MN15-D3BJ"
check_dir = "B3LYP-D3BJ"

for file in os.listdir(folder):
    if not file.endswith(".in"):
        continue
    if file not in os.listdir(check_dir):
        os.remove(os.path.join(folder, file))

for file in os.listdir(folder):
    if file.endswith(".in"):
        continue
    name = file.split(".")[0]
    if name + ".in" not in os.listdir(folder):
        os.remove(os.path.join(folder, file))
