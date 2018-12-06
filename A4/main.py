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

headerText = 'my compressed image - v1.0' # Text at the beginning of the compressed file, to identify it
DELIM = '_' # Delimiter between values in the dictionary ex) 25_56_98
MAX_DICT_LENGTH = 65536 # Maximum length of dictionary

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

  # Here the dictionary key is a string, a concatenation of potentially multiple dictionary entries.
  # The value is the index in the dictionary  
  # This will be updated as the LZW encoding algorithm progresses.
  dictionary = dict()

  # Initialize dictionary values
  init_cmp_dictionary(dictionary)
 
  # Initialize byte array to contain all dictionary indices
  outputBytes = bytearray()
  s = "" # Subsequence

  startTime = time.time()

  for ch in range(numChannels):
    for y in range(yRange):
      for x in range(xRange):
        # Calculate the 'error' (difference) between the previous and current pixel values 
        err = get_err(numChannels, y, x, ch, img)
        
        b = str( int(err) ) # Truncate to int and convert to string
        c = s + DELIM + b # From the notes on LZW encoding, c would be s+x where x is err
       
        if c in dictionary:
          # If c is in the dicitonary we continue and set the subsequence (s) to c
          s = c
        else:
          # If c is not in the dictionary, we append the dictionary index of s to outputBytes,
          # then add c to the dictionary

          # Parse dictionary index into two bytes by converting to binary
          index_dec = dictionary[s]
          index_bin = format(index_dec, '016b') # Convert to binary
          upper = index_bin[8:16]
          lower = index_bin[0:8]
          outputBytes.append( int(lower, 2) ) # Append lower 8 bits 
          outputBytes.append( int(upper, 2) ) # Append upper 8 bits

          if len(dictionary) < MAX_DICT_LENGTH:
            dictionary[c] = len(dictionary) - 1

          s = DELIM + str(b)

  if s:
    # After the main algorithm, if a subsequence still exists we must add it to outputBytes
    # Parse dictionary index into two bytes by converting to binary
    index_dec = dictionary[s]
    index_bin = format(index_dec, '016b') # Convert to binary
    upper = index_bin[8:16]
    lower = index_bin[0:8]
    outputBytes.append( int(lower, 2) ) # Append lower 8 bits 
    outputBytes.append( int(upper, 2) ) # Append upper 8 bits

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

# Init compression dictionary (same as decompression dictionary with key values swapped for ease of use)
def init_cmp_dictionary(dictionary):
  for i in range(0,512):
    value = i-255
    dictionary[ DELIM + str(value) ] = i

# Calculate the 'error' (difference) between the previous and current pixel values 
def get_err(numChannels, y, x, ch, img):
  err = 0
  if numChannels == 1:
    # If the number of channels is 1, we use img[y,x] instead
    # This is only code specific to this case (other than where we set numChannels)
    if x == 0:
    # At the beginning of the column there is no previous pixel
      err = int( img[y,x] )
    else:
      err = int( img[y,x] ) - int( img[y,(x-1)] ) 
  else:
    if x == 0:
      err = int( img[y,x,ch] )
    else:
      err = int( img[y,x,ch] ) - int( img[y,(x-1),ch] ) 

  return err

# Uncompress an image
def uncompress( inputFile, outputFile ):
  # Check that it's a known file
  if inputFile.readline() != headerText + '\n':
    sys.stderr.write( "Input is not in the '%s' format.\n" % headerText )
    sys.exit(1)
    
  # Read the rows, columns, and channels.  
  rows, columns, channels = [ int(x) for x in inputFile.readline().split() ]

  # Read the raw bytes.
  inputBytes = bytearray( inputFile.read() )
  byteIter = iter(inputBytes)
  
  img = np.empty( [rows,columns,channels], dtype=np.uint8 )
  
  # Build the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.

  compressed = [] # List that will contain all the dictionary indices

  # Convert the dictionary indices (that were separated into two separate bytes) back to their original values
  for i in range(0, len(inputBytes), 2):
    # Convert back to binary in order to reconstruct original index
    lower = format(inputBytes[i], '008b') 
    upper = format(inputBytes[i+1], '008b')
    orig_idx = lower + upper # Concatenate upper and lower bits to get original index value
    orig_idx = int(orig_idx,2) # Convert back to int
    compressed.append(orig_idx)

  # Here the dictionary key is the index in the dictionary  
  # The value is a string, a concatenation of potentially multiple dictionary entries.
  # This will be updated as the LZW encoding algorithm progresses.
  dictionary = dict()

  # Initialize dictionary values
  init_dec_dictionary(dictionary)

  w0 = dictionary[compressed[0]].split(DELIM)[1:]
  img[0,0,0] = int(w0[0])
  
  w = w0
  entry = ""
  result = []

  # Initialize image indexes for y position, x position, and channel
  xIndex = 1
  yIndex = 0
  cIndex = 0
  feedbackVal = w0[0]

  startTime = time.time()

  # Loop through key values
  for k in compressed[1:]:
    if k in dictionary:
      # If code is in dictionary
      entry = dictionary[k].split(DELIM)[1:]
    else:
      # If code not in dictionary, T = S+S[0]
      entry = w + [w[0]]

    # Iterate through list of decoded entries and enter into image
    # Move current position of image 
    for currentVal in entry: 
      # If at end of a row, start new row
      if xIndex == columns:
        xIndex = 0
        feedbackVal = 0
        yIndex +=1

        # If at end of column, start new channel
        if yIndex == rows:
          yIndex = 0
          cIndex += 1

          # If at end of channels, stop
          if cIndex == 3:
              cIndex = 2
              break
    
      # Place new value at indexed position in image
      img[yIndex,xIndex,cIndex] = int(feedbackVal) + int(currentVal)
      feedbackVal = int(feedbackVal) + int(currentVal)
      xIndex += 1
    
    # Append S + T[0] to dictionary
    dictionary[len(dictionary)] = DELIM + DELIM.join(w) + DELIM + entry[0]

    # S + T
    w = entry

  endTime = time.time()

  print "Decompressed image size: %d x %d" % (y+1, x)

  # Output the image
  netpbm.imsave( outputFile, img )

  sys.stderr.write( 'Uncompression time: %.2f seconds\n' % (endTime - startTime) )

# Init decompression dictionary (same as compression dictionary with key values swapped for ease of use)
def init_dec_dictionary(dictionary):
  for i in range(0,511):
    value = i-255
    dictionary[i] = DELIM + str(value)

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


