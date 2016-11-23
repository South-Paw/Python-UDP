```
University of Canterbury
COSC264 Assignment
20th September 2015
```

# Python UDP
Created for a networking course, this is an example of a simple UDP
application in Python 3 consisting of a `sender`, `channel` and a `receiver`.

This was written to an assignment specification however I don't seem to have a
copy of the assignment PDF anymore.

## How to run
You'll need 3 command prompts or terminal windows each running one Python file

1. Run the `channel.py` as follows;
  * Usage: `python3 channel.py <csin_port> <csout_port> <crin_port> <crout_port> <sin_port> <rout_port> <drop_rate> <hash>`
  * Example: `python3 channel.py 5006 5005 5007 5008 5004 5001 0.01 somehash`
2. Run the `receiver.py` as follows;
  * Usage: `python3 receiver.py <rin_port> <rout_port> <crin_port> <file_to_receive>`
  * Example: `python3 receiver.py 5001 5002 5007 testOut.dat`
3. Run the `sender.py` as follows;
  * Usage: `python3 sender.py <sin_port> <sout_port> <csin_port> <file_to_send>`
  * Example: `python3 sender.py 5004 5003 5006 file.dat`

The parameter names aren't exactly the most descriptive but try matching up the
port numbers to see who is talking to who.
