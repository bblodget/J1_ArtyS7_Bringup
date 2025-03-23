// Test for 2dup vs. 2 dup

include "core/j1_base_macros.asm"

3 5
2dup+    // Should treat this as a single word (stack: 3 5 8)
2 dup    // Should treat this as the number 2 followed by dup (stack: 3 5 8 2 2) 
+       // Stack should now be: 3 5 8 4
+       // Stack should now be: 3 5 12
+       // Stack should now be: 3 17
+       // Stack should now be: 20
drop    // Stack should now be empty
