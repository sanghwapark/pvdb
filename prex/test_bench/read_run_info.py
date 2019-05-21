runinfo_file=".runstart.info"

"""
format

[Run]
type:Test

[beam]
current:70
energy:1.063
polarization:90
raster:off

[comment]
text:test of DAQ

[dithering]
magnet:off
magnets:

[leftarm]
p:1.063
theta:5

[parity]
feedback:off
ihwp:in

[rightarm]
p:1.063
theta:5

[target]
fanspeed:0 Hz
type:No Target, Empty

"""

ddict={}
new_field=False
with open(runinfo_file, "rb") as f:
    output = f.read()
    d_info = filter(None, [x.strip() for x in output.strip().split("[")])
    for l in d_info:
        fd = l.split("]\n",1)[0]
        ddict[fd] = {}
        for cont in [x.strip() for x in l.split("]\n",1)[1].split("\n")]:
            group=cont.split(":",1)[0]
            var=cont.split(":",1)[1]    
            ddict[fd][group] = var

print ddict["Run"]["type"]
