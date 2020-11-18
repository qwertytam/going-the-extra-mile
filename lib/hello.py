import os, sys, tempfile, time

with tempfile.TemporaryDirectory() as tmpdirname:
    print('created temporary directory', tmpdirname)

    f = tempfile.TemporaryFile(dir = tmpdirname)
    f.write(b'Welcome to TutorialsPoint')

    f.seek(os.SEEK_SET)
    print(f.read())
    print(f.name)
    time.sleep(60)
    f.close()
