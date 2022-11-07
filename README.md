# BlockChain_Ex1
## Requirements: 
  ```
  pip install requests
  ```

## Usage:
```
python blockchain.py <timestamp>
```
## Description:
The system uses an estimate of the amount of blocks created between the timestamp given and the time in the Genesis Block.
It calculates relatively tighter upper & lower boundaries, then uses a binary search to return the desired block's height.



## Stats:
Tested the performance of 3 different aproaches over 30
iterations.


|   	|fixed growth rate|current growth rate|simple bisect   	|   	
|---	|---	|---	|---	|
|total calls|593   	|764   	|599   	|   	
|calls / run|19.8   	|25.5   	|19.9   	|