CISC 457 Assignment 2

Nat Wong - 10137044 - 13nrw5
Wyatt Wood - 10129798 - 13ww11

The equations in class for angle and distance did not give us the correct answer so we had to modify them (adding or subtracting 90 from the angle, different distance equation for line 2). 
We weren't sure if our dataset was wrong from the previous parts, or if we were implementing the equations incorrectly, so we submitted with incorrect numbers for line 2 distances.


We also were not certain if you were meant to still sort the angles as mentioned in class because it didn't seem to give the correct solution either.
However we've provided that code below since it was mentioned in class:


angDist  = []	  # [angle, distance]

# This line was inside the loop and would append for each angle and distance
angDist.append([angle,distance]) # Append to angles, distances list

# Sort angDist list based on angle
  sortedList = sorted(angDist, key=takeFirst)

  # Find index that separates Line 1 from Line 2
  idx = 0
  for i in range(0,len(angDist)-1):
    if np.absolute(sortedList[i][0] - sortedList[i+1][0]) > 50:
	  # Compare angle to previous angle, if the difference is greater than 50 this is where we split the list
      idx = i+1
      break
  
  # Split list based on angle
  angDist1 = sortedList[0:idx]
  angDist2 = sortedList[idx:len(angDist)]