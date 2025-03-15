// Test for 2dup vs. 2 dup

include "core/j1_base_macros.asm"

2dup     // Should treat this as a single word (duplicate top 2 stack items)
2 dup    // Should treat this as the number 2 followed by dup 

8           // Stack: 8
5           // Stack: 8 5
+            // Stack: 13