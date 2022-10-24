import upip

def installDeps():
    f = open("requirements.txt", "r")
    for line in f:
        upip.install(line)
