N[d-1]          // drop     N -> T, dec stack size
T[T->N,d+1]     // dup      T -> T, Copy TOS to NOS, inc stack size
T               // noop     T -> T
N[T->N]         // swap     N -> T, Copy TOS to NOS
N[T->N,d+1]     // over     N -> T, Copy TOS to NOS, inc stack size
T[d-1]          // nip      T -> T, dec stack size

