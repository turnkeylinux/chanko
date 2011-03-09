
import os

def mkdir(path):
    path = str(path)
    if not os.path.exists(path):
        os.makedirs(path)

