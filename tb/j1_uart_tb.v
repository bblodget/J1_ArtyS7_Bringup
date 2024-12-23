`timescale 1ns / 1ps

module j1_uart_tb();

    // Testbench signals
    reg clk;
    reg resetq;
    wire io_rd;
    wire io_wr;
    wire [15:0] io_addr;
    wire [15:0] io_dout;
    reg [15:0] io_din;
    reg interrupt_request;

    // UART test data
    reg [7:0] test_char = 8'h41;  // ASCII 'A'
    reg uart_data_valid = 1'b1;    // Data is available

    // Handle UART read operations
    always @(*) begin
        if (io_rd && io_addr == 16'h4000) begin
            // Return test character when reading from UART_RX
            io_din = uart_data_valid ? {8'h00, test_char} : 16'h0000;
        end else begin
            io_din = 16'h0000;
        end
    end

    // Monitor UART writes
    always @(posedge clk) begin
        if (io_wr && io_addr == 16'h4001) begin
            $display("UART TX: %c (0x%h) at time %0t", io_dout[7:0], io_dout[7:0], $time);
        end
    end

    // Instantiate the J1 processor
    j1 uut (
        .clk(clk),
        .resetq(resetq),
        .io_rd(io_rd),
        .io_wr(io_wr),
        .io_addr(io_addr),
        .io_dout(io_dout),
        .io_din(io_din),
        .interrupt_request(interrupt_request)
    );

    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Test stimulus
    initial begin
        // Initialize signals
        resetq = 0;
        io_din = 0;
        interrupt_request = 0;

        // Wait 100ns for global reset
        #100;
        
        // Release reset
        resetq = 1;

        // Run for 20 clock cycles
        repeat(20) @(posedge clk);

        // Test complete
        $display("Test complete");
        $finish;
    end

    // Monitor PC, instruction, and stack top
    initial begin
        $display("Time\tPC\t\tInstruction\tStack Top");
        $display("----------------------------------------");
        $monitor("%0t\t%h\t%h\t%h", 
                 $time, 
                 uut.pc, 
                 uut.insn, 
                 uut.st0);
    end

endmodule