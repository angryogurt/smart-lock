import subprocess

print("gpio write 30 1")
bashCommand = "gpio write 30 1"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()