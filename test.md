### Progress reporting

Per our earlier agreement: print the name of the first entry decoded, then
every 1000th one after that. This is purely a sanity check that decoding is
keeping up across ~580k total records ( 525,557 files + 56,216 folders, per
your NDIR32 count), not a real progress bar.
