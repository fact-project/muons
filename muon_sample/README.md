# Muon sample

A list of (almost) all events recorded by FACT that are likely to be muon events. Currently this contains 13.78 millon muons. Not all events are yet taken into account, there is a gap from '''20141101''' until '''20150401''', which is currently processed.

### Format
A gzipped binary file named '''event_ids.gz'''. Each Even ID chunk is 12bytes in size and contains 3 unsigned integers:
```
[ uint32: Night, unint32: Run, uint32: Event ]
```
