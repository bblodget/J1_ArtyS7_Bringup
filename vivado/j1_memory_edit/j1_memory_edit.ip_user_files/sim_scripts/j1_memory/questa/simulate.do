onbreak {quit -f}
onerror {quit -f}

vsim  -lib xil_defaultlib j1_memory_opt

set NumericStdNoWarnings 1
set StdArithNoWarnings 1

do {wave.do}

view wave
view structure
view signals

do {j1_memory.udo}

run 1000ns

quit -force
