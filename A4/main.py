# Image compression
#
# You'll need Python 2.7 and must install these packages:
#
#   scipy, numpy
#
# You can run this *only* on PNM images, which the netpbm library is used for.
#
# You can also display a PNM image using the netpbm library as, for example:
#
#   python netpbm.py images/cortex.pnm

import sys, os, math, time, netpbm
import numpy as np

# Text at the beginning of the compressed file, to identify it
headerText = 'my compressed image - v1.0'

# Compress an image
def compress( inputFile, outputFile ):
  # Read the input file into a numpy array of 8-bit values
  #
  # The img.shape is a 3-type with rows,columns,channels, where
  # channels is the number of component in each pixel.  The img.dtype
  # is 'uint8', meaning that each component is an 8-bit unsigned
  # integer.
  img = netpbm.imread( inputFile ).astype('uint8')
  
  # Compress the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO FILL THE 'outputBytes' ARRAY.
  #
  # Note that single-channel images will have a 'shape' with only two
  # components: the y dimensions and the x dimension.  So you will
  # have to detect this and set the number of channels accordingly.
  # Furthermore, single-channel images must be indexed as img[y,x]
  # instead of img[y,x,1].  You'll need two pieces of similar code:
  # one piece for the single-channel case and one piece for the
  # multi-channel case.

  # Number of rows and columns in img
  yRange = img.shape[0]
  xRange = img.shape[1]

  # Number of channels in img
  if len(img.shape) > 2:
    numChannels = img.shape[2]
  else:
    numChannels = 1

  # Print image stats to the terminal
  print "This image has %d channel(s)" % numChannels
  print "This image is %d x %d" % (yRange, xRange)

  # Dictionary containing Key, String pairs. 
  # Here the key is the index in the dictionary, and the String is the concatenation of potentially multiple dictionary entries. 
  # This will be updated as the LZW algorithm progresses.
  dictionary = dict()

  # Initialize dictionary values (-255 -> 255)
  init_cmp_dictionary(dictionary)
 
  outputBytes = bytearray()
  s = "" # Subsequence

  startTime = time.time()

  for ch in range(numChannels):
    for y in range(yRange):
      for x in range(xRange):
        if numChannels == 1:
          if x == 0:
            err = int(img[y,x])
          else:
            err = int(img[y,x]) - int(img[y,(x-1)]) 
        else:
          if x == 0:
            err = int(img[y,x,ch])
          else:
            err = int(img[y,x,ch]) - int(img[y,(x-1),ch]) 
        
        b = str(int(err))
        c = a + 'x' + b
       
        if c in dictionary:
          a = c
        else:
          binary = format(dictionary[a], '016b')
          outputBytes.append(int(binary[0:8], 2))
          outputBytes.append(int(binary[8:16], 2))

          if len(dictionary) < 65536:
            dictionary[c] = len(dictionary) - 1

          a = 'x' + str(b)

  if a:
    binary = format(dictionary[a], '016b')
    outputBytes.append(int(binary[0:8], 2))
    outputBytes.append(int(binary[8:16], 2))

  endTime = time.time()

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.
  outputFile.write( '%s\n'       % headerText )

  # Handle 1 channel images
  if len(np.shape(img)) == 2:
    outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], 1) )
  else:
    outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]) )

  outputFile.write( outputBytes )

  # Print information about the compression
  if len(np.shape(img)) == 2:
    inSize  = img.shape[0] * img.shape[1]
  else:
    inSize  = img.shape[0] * img.shape[1] * img.shape[2]

  outSize = len(outputBytes)

  sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
  sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
  sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
  sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )

# Initialize dictionary with values -255 to 256, indexed with 0-511
def init_cmp_dictionary(dictionary):
  for i in range(0,512):
    value = i-255
    dictionary["x" + str(value)] = i

def init_dec_dictionary(dictionary):
  # Init dictionary with values -255 to 255, indexed with 0-511
  dictIndex = 0
  for d in range(-255, 256):
    dictionary[dictIndex] = "x" + str(d)
    dictIndex += 1

# Uncompress an image
def uncompress( inputFile, outputFile ):
  # Check that it's a known file

  if inputFile.readline() != headerText + '\n':
    sys.stderr.write( "Input is not in the '%s' format.\n" % headerText )
    sys.exit(1)
    
  # Read the rows, columns, and channels.  
  rows, columns, channels = [ int(x) for x in inputFile.readline().split() ]

  # Read the raw bytes.
  inputBytes = bytearray(inputFile.read())
  byteIter = iter(inputBytes)

  compressed = []

  # Get the indices in decimal format (inputBytes stores them in 2 separate bytes)
  for i in range(0,len(inputBytes),2):
    bin1 = format(inputBytes[i], '008b')
    bin2 = format(inputBytes[i+1], '008b')
    binary = bin1 + bin2
    num = int(binary,2)
    compressed.append(num)

  print "Length of inputBytes in decimal:", len(compressed)
  
  # Build the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.

  dictionary = dict() # Dictionary containing Key, List pairs
  init_dec_dictionary(dictionary) # Initialize dictionary values (-256 -> 255)

  startTime = time.time()
  img = np.empty( [rows,columns,channels], dtype=np.uint8 )

  w0 = dictionary[compressed[0]].split('x')[1:]
  img[0,0,0] = int(w0[0])
  
  w = w0
  entry = ""
  result = []

  count = 0

  x = 1
  y = 0
  c = 0
  pp = w0[0]

  for k in compressed[1:]:
    if k in dictionary:
      # If code is in dictionary
      entry = dictionary[k].split('x')[1:]
    else:
      # If code not in dictionary, T = S+S[0]
      entry = w + [w[0]]

    for i in entry: 
      if x == columns:
        x = 0
        pp = 0
        y +=1
        if y == rows:
          y = 0
          c += 1
          if c == 3:
              c = 2
              break
    
      img[y,x,c] = int(pp) + int(i)
      #print img[y,x,c]
      pp = int(pp) + int(i)
      x += 1
    #print x,y,img[y,x,c]
    
    # Append S + T[0] to dictionary
    dictionary[len(dictionary)] = 'x' + 'x'.join(w) + 'x' + entry[0]

    #S + T
    w = entry

  endTime = time.time()

  print "Decompressed image size: %d x %d" % (y+1, x)

  # Output the image
  netpbm.imsave( outputFile, img )

  sys.stderr.write( 'Uncompression time: %.2f seconds\n' % (endTime - startTime) )

# The command line is 
#
#   main.py {flag} {input image filename} {output image filename}
#
# where {flag} is one of 'c' or 'u' for compress or uncompress and
# either filename can be '-' for standard input or standard output.


if len(sys.argv) < 4:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)

# Get input file
 
if sys.argv[2] == '-':
  inputFile = sys.stdin
else:
  try:
    inputFile = open( sys.argv[2], 'rb' )
  except:
    sys.stderr.write( "Could not open input file '%s'.\n" % sys.argv[2] )
    sys.exit(1)

# Get output file

if sys.argv[3] == '-':
  outputFile = sys.stdout
else:
  try:
    outputFile = open( sys.argv[3], 'wb' )
  except:
    sys.stderr.write( "Could not open output file '%s'.\n" % sys.argv[3] )
    sys.exit(1)

# Run the algorithm

if sys.argv[1] == 'c':
  compress( inputFile, outputFile )
elif sys.argv[1] == 'u':
  uncompress( inputFile, outputFile )
else:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)


