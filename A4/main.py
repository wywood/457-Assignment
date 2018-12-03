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
dictionary = dict()
start_2D = 513
start_3D = -1
skip_first = True

# Compress an image
def compress( inputFile, outputFile ):
  # Read the input file into a numpy array of 8-bit values
  #
  # The img.shape is a 3-type with rows,columns,channels, where
  # channels is the number of component in each pixel.  The img.dtype
  # is 'uint8', meaning that each component is an 8-bit unsigned
  # integer.

  img = netpbm.imread( inputFile ).astype('uint8')
  
  y_range = img.shape[0]
  x_range = img.shape[1]
  
  if len(img.shape) > 2:
    numChannels = img.shape[2]
  else:
    numChannels = 1

  numChannels = 1
    
  init_dictionary()
  
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

  w1 = 0.333333
  w2 = 0.5

  startTime = time.time()

  outputBytes = bytearray(0)
  S = []
  temp = []
  last_idx = -1
  curr_idx = -1

  for c in range(numChannels):
    for y in range(y_range):
      startTime = time.time()
      for x in range(x_range):
        if x == 0:
            print y
        #if (x+1) >= x_range:
        #  X = img[y+1,0,c]
        #else:
        #  X = img[y,x+1,c]
        
        if y-1 >= 0 and x-1 >= 0:
            err = img[y,x,c] - (w1 * img[y-1,x-1,c] + w1 * img[y-1,x,c] + w1 * img[y,x-1,c])
        elif x-1 >= 0:
            err = img[y,x,c] - img[y,x-1,c]
        elif y-1 >= 0:
            err = img[y,x,c] - (w2 * img[y-1,x-1,c] + w2 * img[y-1,x,c])
        else:
            err = img[y,x,c] # TODO???
            print "Everything is out of bounds!"

        X = int(err)

        temp = list(S)
        temp.append(X)

        curr_idx = in_dictionary(temp)
        #print ('idx: %d' % curr_idx)
        #print "S: "
        #print S
        #print "temp: "
        #print temp
        #print ""

        if (curr_idx != -1):
          last_idx = curr_idx
          S = list(temp)
          #print "newS: "
          #print S
          #print ""
        else:
          append = in_dictionary(S)

          global start_3D
          if len(S) >= 3 and not skip_first:
            print "hey"
            start_3D = len(dictionary)
          #print S
          #print temp
          #print ('append: %d' % append)
          #print ""
          if append != -1:
            if append < 256:
                outputBytes.append( 0 ) # Append all zeros for the upper 8 bits 
                outputBytes.append( append ) # Lower 8 bits
            else:
                outputBytes.append(append >> 8)
                outputBytes.append(255)
            dictionary[len(dictionary)] = list(temp)
            S = [X]
          else:
            print "Couldn't find index"
            print S
            dictionary[len(dictionary)] = list(S) # TODO
            S = [X]
          print dictionary
          print ""
          global dictionary
          sorted_list = sorted(dictionary.items(), key= lambda e: e[1][0])
          print sorted_list
          print ""
          print ""
      endTime = time.time()

      print endTime-startTime

  print np.uint8(outputBytes)
  endTime = time.time()

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.

  outputFile.write( '%s\n'       % headerText )
  outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]) )
  outputFile.write( outputBytes )

  # Print information about the compression
  
  inSize  = img.shape[0] * img.shape[1] * img.shape[2]
  outSize = len(outputBytes)

  sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
  sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
  sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
  sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )

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

  # Build the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.

  startTime = time.time()

  img = np.empty( [rows,columns,channels], dtype=np.uint8 )

  byteIter = iter(inputBytes)
  for y in range(rows):
    for x in range(columns):
      for c in range(channels):
        img[y,x,c] = byteIter.next()

  endTime = time.time()

  # Output the image

  netpbm.imsave( outputFile, img )

  sys.stderr.write( 'Uncompression time: %.2f seconds\n' % (endTime - startTime) )

# Detect if sequence exists in dictionary
def in_dictionary( seq ):
  idx = -1

  global skip_first

  if len(seq) == 1:
    start = 0
  elif len(seq) > 1:
    start = start_2D

  for i in range( start, len(dictionary) ):
    idx = -1
    dict_seq = dictionary[i]

    if len(dict_seq) <= 0 or len(seq) <= 0 or len(dict_seq) != len(seq):
      continue

    for x in range( len(dict_seq) ):
      if x <= len(seq) and seq[x] == dict_seq[x]:
        idx = i
      else:
        idx = -1
        break
      
    if idx != -1:
      break
  
  return idx

def init_dictionary():
  # Init dictionary with values -255 to 255, indexed with 0-511
  #for i in range(0,10):
  #    value = [i-25]
  #    dictionary[i] = value
  for i in range(0,512):
    value = [i-256]
    dictionary[i] = value

def take_first(seq):
  return seq[0]

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
