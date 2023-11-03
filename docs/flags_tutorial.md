* find value that changes by comparing file before and after the change
* get attributes bytes (00 10 87) -> size: 3
* get the byte you are interested in (10) -> attributes[1]
* convert 10 to binary -> 00010000
* calculate the shift to the left -> 1 << 4
* attributes[1] & (1 << 4) != 0