'''
read and update uptime value, this script will be called from a crontab jpb every 1 minute
'''

with open('/home/pi/dev/scp_v2/uptime.txt','r+') as f:
    time = int(f.read())
    f.seek(0)
    print(time)
    time += 1
    f.write(str(time))

