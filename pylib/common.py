
import os
import md5

def mkdir(path):
    path = str(path)
    if not os.path.exists(path):
        os.makedirs(path)

def md5sum(path):
    if os.path.exists(path):
        return md5.md5(file(path, 'rb').read()).hexdigest()

    return False
