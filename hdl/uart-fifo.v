`include "config.vh"
`default_nettype none

/*
 *  PicoSoC - A simple example SoC using PicoRV32
 *
 *  Copyright (C) 2017  Clifford Wolf <clifford@clifford.at>
 *
 *  Permission to use, copy, modify, and/or distribute this software for any
 *  purpose with or without fee is hereby granted, provided that the above
 *  copyright notice and this permission notice appear in all copies.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 *  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 *  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 *  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 *  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 *  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 *  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 */

// October 2019, Matthias Koch: Renamed wires and added FIFO on receive side

module buart (
    input  wire       clk,      // Clock input
    input  wire       resetq,   // Active-low reset
    output wire       tx,       // UART transmit pin
    input  wire       rx,       // UART receive pin
    input  wire       rd,       // Read strobe - set high to read from RX FIFO
    input  wire       wr,       // Write strobe - set high to write to TX
    input  wire [7:0] tx_data,  // Data to transmit
    output wire [7:0] rx_data,  // Received data
    output wire       busy,     // High when transmitter is busy
    output wire       valid     // High when received data is available
);

    reg [3:0] recv_state;
    reg [$clog2(`cfg_divider)-1:0] recv_divcnt;   // Counts to cfg_divider. Reserve enough bytes !
    reg [7:0] recv_pattern;

    reg [9:0] send_pattern;
    reg [3:0] send_bitcnt;
    reg [$clog2(`cfg_divider)-1:0] send_divcnt;   // Counts to cfg_divider. Reserve enough bytes !
    reg send_dummy;

    reg [7:0] empfangenes [7:0]; // 8 Bytes Platz im Puffer
    reg [2:0] lesezeiger;
    reg [2:0] schreibzeiger;

    assign rx_data = empfangenes[lesezeiger];
    assign valid = ~(lesezeiger == schreibzeiger);
    assign busy = (send_bitcnt || send_dummy);

    always @(posedge clk) begin
        if (!resetq) begin
            recv_state <= 4'd0;
            recv_divcnt <= 0;
            recv_pattern <= 8'd0;
            lesezeiger <= 3'd0;
            schreibzeiger <= 3'd0;
        end else begin
            recv_divcnt <= recv_divcnt + 1;

            if (rd) lesezeiger <= lesezeiger + 1;

            case (recv_state)
                0: begin
                    if (!rx)
                        recv_state <= 4'd1;
                    recv_divcnt <= 0;
                end
                1: begin
                    if (2*recv_divcnt > `cfg_divider) begin
                        recv_state <= 4'd2;
                        recv_divcnt <= 0;
                    end
                end
                10: begin
                    if (recv_divcnt > `cfg_divider) begin
                        empfangenes[schreibzeiger] <= recv_pattern;
                        schreibzeiger <= schreibzeiger + 1;
                        recv_state <= 4'd0;
                    end
                end
                default: begin
                    if (recv_divcnt > `cfg_divider) begin
                        recv_pattern <= {rx, recv_pattern[7:1]};
                        recv_state <= recv_state + 1;
                        recv_divcnt <= 0;
                    end
                end
            endcase
        end
    end

    assign tx = send_pattern[0];

    always @(posedge clk) begin
        send_divcnt <= send_divcnt + 1;
        if (!resetq) begin
            send_pattern <= 10'h3ff;
            send_bitcnt <= 4'd0;
            send_divcnt <= 0;
            send_dummy <= 1'b1;
        end else begin
            if (send_dummy && !send_bitcnt) begin
                send_pattern <= 10'h3ff;
                send_bitcnt <= 4'd15;
                send_divcnt <= 0;
                send_dummy <= 1'b0;
            end else
            if (wr && !send_bitcnt) begin
                send_pattern <= {1'b1, tx_data[7:0], 1'b0};
                send_bitcnt <= 4'd10;
                send_divcnt <= 0;
            end else
            if (send_divcnt > `cfg_divider && send_bitcnt) begin
                send_pattern <= {1'b1, send_pattern[9:1]};
                send_bitcnt <= send_bitcnt - 1;
                send_divcnt <= 0;
            end
        end
    end

    // Debug signals
    reg [3:0] dbg_state;
    always @(posedge clk) begin
        dbg_state <= recv_state;
        if (recv_state != dbg_state)
            $display("Time=%0t UART state change: %d -> %d", $time, dbg_state, recv_state);
        
        if (rd)
            $display("Time=%0t UART FIFO read: data=%h ptr=%d", 
                    $time, rx_data, lesezeiger);
        if (schreibzeiger != lesezeiger)
            $display("Time=%0t UART FIFO status: write_ptr=%d read_ptr=%d", 
                    $time, schreibzeiger, lesezeiger);
    end

endmodule
