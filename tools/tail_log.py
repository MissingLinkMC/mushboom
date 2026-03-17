import time

f = open("logs/mushboom.log")
f.seek(0, 2)
while True:
    line = f.readline()
    if line:
        print(line, end="")
    else:
        time.sleep(0.5)
