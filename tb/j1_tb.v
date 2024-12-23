`timescale 1ns / 1ps

module j1_tb();

    // Testbench signals
    reg clk;
    reg resetq;
    wire io_rd;
    wire io_wr;
    wire [15:0] io_addr;
    wire [15:0] io_dout;
    reg [15:0] io_din;
    reg interrupt_request;

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

        // Wait for first instruction to complete
        @(posedge clk);
        @(posedge clk); // Extra cycle for memory read
        #1; // Check just after clock edge
        if (uut.st0 !== 16'h0001) $display("Error: Expected 0x0001, got %h", uut.st0);
        else $display("Success: Push 0x0001");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h0002) $display("Error: Expected 0x0002, got %h", uut.st0);
        else $display("Success: Push 0x0002");

        // Continue pattern for remaining values...
        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h0003) $display("Error: Expected 0x0003, got %h", uut.st0);
        else $display("Success: Push 0x0003");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h0004) $display("Error: Expected 0x0004, got %h", uut.st0);
        else $display("Success: Push 0x0004");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h0005) $display("Error: Expected 0x0005, got %h", uut.st0);
        else $display("Success: Push 0x0005");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h0006) $display("Error: Expected 0x0006, got %h", uut.st0);
        else $display("Success: Push 0x0006");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h0007) $display("Error: Expected 0x0007, got %h", uut.st0);
        else $display("Success: Push 0x0007");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h0008) $display("Error: Expected 0x0008, got %h", uut.st0);
        else $display("Success: Push 0x0008");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h0009) $display("Error: Expected 0x0009, got %h", uut.st0);
        else $display("Success: Push 0x0009");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h000A) $display("Error: Expected 0x000A, got %h", uut.st0);
        else $display("Success: Push 0x000A");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h000B) $display("Error: Expected 0x000B, got %h", uut.st0);
        else $display("Success: Push 0x000B");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h000C) $display("Error: Expected 0x000C, got %h", uut.st0);
        else $display("Success: Push 0x000C");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h000D) $display("Error: Expected 0x000D, got %h", uut.st0);
        else $display("Success: Push 0x000D");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h000E) $display("Error: Expected 0x000E, got %h", uut.st0);
        else $display("Success: Push 0x000E");

        @(posedge clk);
        #1;
        if (uut.st0 !== 16'h000F) $display("Error: Expected 0x000F, got %h", uut.st0);
        else $display("Success: Push 0x000F");

        // Test complete
        #100;
        $display("Test complete");
        $finish;
    end

    // Optional: Monitor stack operations
    initial begin
        $monitor("Time=%0t st0=%h dsp=%0d insn=%h", $time, uut.st0, uut.dsp, uut.insn);
    end

endmodule