import urllib
from peopleflow.helpers.printlabel import *
from .. import app
import hashlib

def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]

def upload(url, folder='images'):
    file = urllib.urlopen(url).read()
    filename = hashlib.md5(file).hexdigest()
    filepath = os.path.join(app.config['STATIC_UPLOAD_FOLDER'], folder, filename)
    with open(filepath, 'wb') as f:
        f.write(file)
        f.close()
    return filename

def delete_upload(filename, folder='images'):
    os.remove(os.path.join(app.config['STATIC_UPLOAD_FOLDER'], folder, filename))