CISC 457 Assignment 3

Nat Wong - 10137044 - 13nrw5
Wyatt Wood - 10129798 - 13ww11

Notes for the TA:
 - We didn't use offset[][] in the trackEdges function because we wanted to use our cool for loop for iterating through neighbourhood pixels:
   for y in range(0-radius,radius+1):
    for x in range(0-radius,radius+1):
