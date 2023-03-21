import subprocess

n = 5
name = "Bot"


for i in range(1, n+1):
    #Thread(target=run_client, args=(i,))
    subprocess.Popen(["gradlew", "run", f"--args={name}{i}", "&"], cwd="C:\\2009scape-master\\client", shell=True)