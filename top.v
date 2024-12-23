`default_nettype none

module top (
    // Board clock and reset
    input  wire clk_12mhz,       // 12MHz clock from board
    input  wire reset,           // Active-high reset from board
    
    // UART pins
    output wire uart_tx,         // UART transmit pin
    input  wire uart_rx,          // UART receive pin

    // LEDs
    output wire [3:0] led
);

    // Clock and reset
    wire sys_clk;               // System clock (12MHz)
    wire sys_rst_n;            // System reset (synchronized)
    
    // UART interface signals
    wire [15:0] uart_dout;     // Data from UART to CPU
    wire [15:0] uart_dout_cpu;     // Data from UART to CPU
    wire [15:0] uart_din;      // Data from CPU to UART
    wire [15:0] uart_addr;     // Address from CPU
    wire uart_rd;              // Read strobe
    wire uart_wr;              // Write strobe
    wire uart_valid;           // UART has data available
    wire uart_busy;            // UART is busy transmitting

    // UART address decoding
    localparam UART_RX_ADDR    = 16'h4000;  // Read UART data
    localparam UART_TX_ADDR    = 16'h4001;  // Write UART data
    localparam UART_VALID_ADDR = 16'h4002;  // Check if UART has data
    localparam UART_BUSY_ADDR  = 16'h4003;  // Check if UART is busy
    
    wire uart_rx_sel   = (uart_addr == UART_RX_ADDR);
    wire uart_tx_sel   = (uart_addr == UART_TX_ADDR);
    wire uart_valid_sel = (uart_addr == UART_VALID_ADDR);
    wire uart_busy_sel  = (uart_addr == UART_BUSY_ADDR);
    
    // Decode UART read/write enables
    wire uart_rd_en = uart_rd & uart_rx_sel;
    wire uart_wr_en = uart_wr & uart_tx_sel;
    
    // Use 12MHz clock directly
    assign sys_clk = clk_12mhz;
    assign sys_rst_n = ~reset;

    // Instantiate J1 CPU
    wire [15:0] cpu_st0;  // Add wire for st0
    j1 cpu (
        .clk(sys_clk),
        .resetq(sys_rst_n),
        
        // I/O interface
        .io_rd(uart_rd),
        .io_wr(uart_wr),
        .io_addr(uart_addr),
        .io_dout(uart_din),     // CPU -> UART
        .io_din(uart_dout_cpu),     // UART -> CPU
        
        .interrupt_request(1'b0), // No interrupts for now

        // Connect st0 for LED display
        .st0(cpu_st0)           // Add port for st0
    );

    // Connect LEDs to lower 4 bits of st0
    assign led = cpu_st0[3:0];

    // Instantiate UART
    buart uart (
        .clk(sys_clk),
        .resetq(sys_rst_n),
        
        // UART pins
        .tx(uart_tx),
        .rx(uart_rx),
        
        // CPU interface
        .rd(uart_rd_en),        // Only read when address matches
        .wr(uart_wr_en),        // Only write when address matches
        .tx_data(uart_din[7:0]),    // Only use lower 8 bits for UART
        .rx_data(uart_dout[7:0]),   // Zero-extend received byte to 16 bits
        .busy(uart_busy),
        .valid(uart_valid)
    );

    // Zero-extend the UART rx_data to 16 bits
    assign uart_dout[15:8] = 8'b0;

    // Status registers
    assign uart_dout_cpu = uart_rx_sel ? (uart_valid ? uart_dout : 16'h0000) :
                          uart_valid_sel ? {15'b0, uart_valid} :
                          uart_busy_sel ? {15'b0, uart_busy} :
                          16'h0000;

endmodule