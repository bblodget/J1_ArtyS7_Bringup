; Test file for Memory/IO and System operations
; Tests memory operations (@, !), IO operations (IO@, IO!),
; and system operations (DINT, EINT, DEPTH, RDEPTH)

main:
    ; Test memory operations
    CALL test_mem_store_fetch DROP
    CALL test_mem_store_fetch_ret DROP

    ; Test IO operations
    ;CALL test_io_store_fetch DROP
    ;CALL test_io_store_fetch_ret DROP

    ; Test system operations
    CALL test_depth DROP
    CALL test_rdepth DROP
    ;CALL test_interrupts DROP

    JMP main

; Memory Operations Tests
test_mem_store_fetch:
    ; Store value 42 to memory location 100
    #42             ; Push value to store
    #100            ; Push address
    !               ; Store to memory
    
    #100            ; Push address again
    @               ; Fetch from memory
    RET             ; Should return 42

test_mem_store_fetch_ret:
    ; Same as above but with +RET optimization
    #42             ; Push value to store
    #100            ; Push address
    !               ; Store to memory
    
    #100            ; Push address again
    @+RET           ; Fetch from memory and return

; IO Operations Tests
test_io_store_fetch:
    ; Write 55 to IO port 1, then read it back
    #55             ; Push value to write
    #1              ; Push IO port number
    IO!             ; Write to IO port
    
    #1              ; Push IO port number again
    IO@             ; Read from IO port
    RET             ; Should return 55

test_io_store_fetch_ret:
    ; Same as above but with +RET optimization
    #55             ; Push value to write
    #1              ; Push IO port number
    IO!             ; Write to IO port
    
    #1              ; Push IO port number again
    IO@+RET         ; Read from IO port and return

; Stack Depth Tests
test_depth:
    ; Test DEPTH operation
    #1              ; Push some values
    #2              ; to create a known
    #3              ; stack depth
    DEPTH           ; Get stack depth
    NIP NIP NIP     ; Clean up stack
    RET             ; Should return 3

test_rdepth:
    ; Test RDEPTH operation
    >R              ; Push to return stack
    >R              ; twice
    RDEPTH          ; Get return stack depth
    R> R>           ; Clean up return stack
    RET             ; Should return 2

; Interrupt Control Tests
test_interrupts:
    DINT            ; Disable interrupts
    #1              ; Push 1 (success marker)
    EINT            ; Re-enable interrupts
    RET             ; Should return 1
