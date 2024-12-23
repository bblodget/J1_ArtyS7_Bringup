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

    // UART and system address decoding
    localparam UART_ADDR      = 16'h1000;  // UART RX/TX at 0x1000
    localparam MISC_IN_ADDR   = 16'h2000;  // UART status at 0x2000
    localparam TICKS_ADDR     = 16'h4000;  // Ticks counter/control at 0x4000
    localparam CYCLES_ADDR    = 16'h8000;  // Cycles counter at 0x8000

    // Add registers for ticks and cycles
    reg [15:0] ticks;
    reg [15:0] cycles;
    wire [16:0] ticks_plus_1 = ticks + 1;
    wire interrupt;

    // Address decoding
    wire uart_sel    = (uart_addr == UART_ADDR);
    wire misc_in_sel = (uart_addr == MISC_IN_ADDR);
    wire ticks_sel   = (uart_addr == TICKS_ADDR);
    wire cycles_sel  = (uart_addr == CYCLES_ADDR);

    // Decode UART read/write enables
    wire uart_rd_en = uart_rd & uart_sel;
    wire uart_wr_en = uart_wr & uart_sel;

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
        
        //.interrupt_request(1'b0), // No interrupts for now
        .interrupt_request(interrupt), // No interrupts for now

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
    assign uart_dout_cpu = 
        uart_sel ? (uart_valid ? {8'b0, uart_dout[7:0]} : 16'h0000) :
        misc_in_sel ? {14'b0, uart_valid, !uart_busy} :
        ticks_sel ? ticks :
        cycles_sel ? cycles :
        16'h0000;

    // Ticks and cycles counter logic
    always @(posedge sys_clk) begin
        if (!sys_rst_n) begin
            ticks <= 16'h0;
            cycles <= 16'h0;
        end else begin
            // Handle ticks counter
            if (uart_wr && ticks_sel)
                ticks <= uart_din;  // Set ticks value
            else
                ticks <= ticks_plus_1[15:0];  // Increment ticks

            // Increment cycles counter
            cycles <= cycles + 1;
        end
    end

    // Generate interrupt on ticks overflow (if needed)
    assign interrupt = ticks_plus_1[16];  // You may need to connect this to the CPU

endmodule