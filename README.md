## image-tool
Short python script for resizing, padding, and cropping images on the command line.

Add it to your .[shell]rc file like so: "alias convert='python .../dir/convert.py'"

# examples
```
>> convert -r "500x500" in.jpg out.png
Starting dimensions, X:2560, Y:1440
Changed dimensions, X:500, Y:500

>> convert -r "50%x50%" in.jpg out.png
Starting dimensions, X:2560, Y:1440
Changed dimensions, X:1280, Y:720

>> convert -r "500*500" in.jpg out.png
Starting dimensions, X:2560, Y:1440
Changed dimensions, X:666, Y:375

>> convert -p "2*Wx2*H" in.jpg out.png
Starting dimensions, X:2560, Y:1440
Changed dimensions, X:5120, Y:2880
```
