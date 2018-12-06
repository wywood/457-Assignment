CISC 457 Assignment 3

Nat Wong - 10137044 - 13nrw5
Wyatt Wood - 10129798 - 13ww11

TA PLEASE NOTE: 
The netpbm.py program doesn't work. We never see any picture displayed, the program simply runs and closes with no error messages seen.
This is possibly an issue with the python or library versions we've installed, we couldn't tell.
We developed on Windows and were running the program from the powershell command line.

Therefore we have included our own version of the netpbm file which we found online, 
with one modification to display single channel images correctly. The proper credit is given in the file.


All results below are using an AMD Ryzen 5 1600 (6C, 12T)

Barbara
  Compression time: 2.17s
  Decompression time: 1.88s
  Compression ratio: 1.27
  Compression ratio of zipped image: 769KB/610KB=1.26

Cortex
  Compression time: 4.59s
  Decompression time: 3.97s
  Compression ratio: 2.83
  Compression ratio of zipped image: 1916KB/414KB=4.63
  Obviously jpg (59KB) and png (215KB) have a much higher compression ratio.

Crest
  Compression time: 11.60s
  Decompression time: 9.84s
  Compression ratio: 10.80
  Compression ratio of zipped image: 5344KB/247KB=21.6

Mandrill
  Compression time: 2.22s
  Decompression time: 1.93s
  Compression ratio: 1.33
  Compression ratio of zipped image: 796KB/600KB=1.3267

Noise
  Compression time: 3.22s
  Decompression time: 2.85s
  Compression ratio: 0.87
  Compression ratio of zipped image: 1025KB/987KB=1.04