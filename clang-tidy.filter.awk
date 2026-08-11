# cat clang-tidy.output.est | gawk -f clang-tidy.filter.awk
# or
# make check 2>&1 | gawk -f ..\clang-tidy.filter.awk
# [ note re-direction of stderr ]
# 
# filter out note: entries in clang-tidy output
# 
# states:
# 0 - no targets found: output = input
#  Suppressed 2026 warnings (1896 in non-user code, 36 NOLINT, 94 with check filters).
# 1 - warning: found: output = input
#  D:/SourceCode/Git/binclock_redux/config.cpp:140:11: warning: Opened stream never closed. Potential resource leak [clang-analyzer-unix.Stream]
# 2 - note: found: discard input
#  D:/SourceCode/Git/binclock_redux/config.cpp:90:8: note: Assuming 'result' is equal to 0
BEGIN {
  state = 0 ;
}
{
   if ($2 == "note:") {
      state = 2 ;
   } 
   else if ($2 == "warning:") {
      state = 1 ;
   }
   else if ($1 == "Suppressed") {
      state = 0 ;
   }
   
   if (state == 2) {
      # do nothing
   }
   else {
      printf("%s\n", $0);
   }
   
}
END { 
}
