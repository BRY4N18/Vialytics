import os

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.sqlite3') or file.endswith('.db'):
            print(os.path.join(root, file))
