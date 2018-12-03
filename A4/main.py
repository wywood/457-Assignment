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
dictionary = dict() # Dictionary containing Key, List pairs
sorted_list = [] # Sorted dictionary
w1 = 0.333333 
w2 = 0.5

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
    
  init_dictionary() # Initialize dictionary values (-256 -> 255)

  # Sort dictionary
  global sorted_list
  sorted_list = sorted(dictionary.items(), key= lambda e: e[1][0])
  
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

  startTime = time.time()

  outputBytes = bytearray(0)
  S = []
  temp = []
  curr_idx = -1

  for c in range(numChannels):
    for y in range(y_range):
      startTime = time.time() # TODO MOVE
      for x in range(x_range):
        if x == 0:
            print y # TODO remove
        
        # Calculate error of predicted from actual
        if y-1 >= 0 and x-1 >= 0:
            err = img[y,x,c] - (w1 * img[y-1,x-1,c] + w1 * img[y-1,x,c] + w1 * img[y,x-1,c])
        elif x-1 >= 0:
            err = img[y,x,c] - img[y,x-1,c]
        elif y-1 >= 0:
            err = img[y,x,c] - (w2 * img[y-1,x-1,c] + w2 * img[y-1,x,c])
        else:
            # TODO???
            continue
            print "All prediction points are out of bounds!"

        # Round to int value
        X = int(err)

        temp = list(S)
        temp.append(X)

        curr_idx = in_dictionary(temp)

        if (curr_idx != -1):
          # If in dictionary
          S = list(temp)
        else:
          # If not in dictionary
          append = in_dictionary(S)

          if append != -1:
            # Split into upper and lower 8 bits
            if append < 256:
                outputBytes.append( 0 ) # Append zeros for the upper 8 bits
                outputBytes.append( append ) # Lower 8 bits
            else:
                outputBytes.append(append >> 8) # Upper 8 bits
                outputBytes.append(append % 256) # Lower 8 bits
            
            dictionary[len(dictionary)] = list(temp)
            S = [X]
          else:
            # TODO
            print "Couldn't find index"
            dictionary[len(dictionary)] = list(S)
            S = [X]

          # Sort list based on new addition
          global sorted_list
          sorted_list = sorted(dictionary.items(), key= lambda e: e[1][0])
      endTime = time.time() # TODO MOVE

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
  #global skip_first
#
#  if len(seq) == 1:
#    start = 0
##  elif len(seq) > 1:
#    start = start_2D

#  for i in range( start, len(dictionary) ):
#    idx = -1
#    dict_seq = dictionary[i]

    #if len(dict_seq) <= 0 or len(seq) <= 0 or len(dict_seq) != len(seq):
     # continue

    #for x in range( len(dict_seq) ):
    #  if x <= len(seq) and seq[x] == dict_seq[x]:
    #    idx = i
    ###  else:
    #    idx = -1
    #    break
    #  
    #if idx != -1:
    #  break
  
  #return idx
  x = seq[0]
  idx = bin_search(0, len(sorted_list)-1, x) # Find starting place for linear search

  print ('start idx: %d' % idx)
  print seq

  if idx != -1:
    # While the first value is still the one we are searching for
    while sorted_list[idx][1][0] == x:
        dict_seq = sorted_list[idx][1] # Get list corresponding to this key
        candidate_idx = idx 

        if len(dict_seq) <= 0 or len(seq) <= 0 or len(dict_seq) != len(seq):
            # Sequences are incompatible, skip this
            idx += 1
            candidate_idx = -1
            continue

        for i in range( len(dict_seq) ):
            # Compare lists for equality
            if seq[i] != dict_seq[i]:
                candidate_idx = -1
                break

        if candidate_idx == -1:
            idx += 1
        else:
            break

    if candidate_idx == -1:
        print -1
        return -1
    else:
        print "Found in dictionary."
        return sorted_list[idx][0]
  else:
    for i in range(len(sorted_list) ):
        idx = -1
        dict_seq = sorted_list[i][1]
        
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
  
    print idx
    return idx

def bin_search(l, r, x):

    while l < r:
        mid = (l + r) // 2
        compare = sorted_list[mid][1][0]
    
        if compare < x:
            l = mid + 1
        elif x < compare:
            r = mid - 1
        else:
            return mid
    
    print "Couldn't find start index."
    return -1

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
