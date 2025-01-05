// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2.1 (win64) Build 5266912 Sun Dec 15 09:03:24 MST 2024
// Date        : Wed Dec 25 17:03:49 2024
// Host        : bbhome running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim c:/Dev/J1_debug/ip_repo/j1_memory_4k/j1_memory_4k_sim_netlist.v
// Design      : j1_memory_4k
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7s50csga324-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "j1_memory_4k,blk_mem_gen_v8_4_10,{}" *) (* downgradeipidentifiedwarnings = "yes" *) (* x_core_info = "blk_mem_gen_v8_4_10,Vivado 2024.2.1" *) 
(* NotValidForBitStream *)
module j1_memory_4k
   (clka,
    wea,
    addra,
    dina,
    douta,
    clkb,
    web,
    addrb,
    dinb,
    doutb);
  (* x_interface_info = "xilinx.com:interface:bram:1.0 BRAM_PORTA CLK" *) (* x_interface_mode = "slave BRAM_PORTA" *) (* x_interface_parameter = "XIL_INTERFACENAME BRAM_PORTA, MEM_ADDRESS_MODE BYTE_ADDRESS, MEM_SIZE 8192, MEM_WIDTH 32, MEM_ECC NONE, MASTER_TYPE OTHER, READ_LATENCY 1" *) input clka;
  (* x_interface_info = "xilinx.com:interface:bram:1.0 BRAM_PORTA WE" *) input [0:0]wea;
  (* x_interface_info = "xilinx.com:interface:bram:1.0 BRAM_PORTA ADDR" *) input [10:0]addra;
  (* x_interface_info = "xilinx.com:interface:bram:1.0 BRAM_PORTA DIN" *) input [15:0]dina;
  (* x_interface_info = "xilinx.com:interface:bram:1.0 BRAM_PORTA DOUT" *) output [15:0]douta;
  (* x_interface_info = "xilinx.com:interface:bram:1.0 BRAM_PORTB CLK" *) (* x_interface_mode = "slave BRAM_PORTB" *) (* x_interface_parameter = "XIL_INTERFACENAME BRAM_PORTB, MEM_ADDRESS_MODE BYTE_ADDRESS, MEM_SIZE 8192, MEM_WIDTH 32, MEM_ECC NONE, MASTER_TYPE OTHER, READ_LATENCY 1" *) input clkb;
  (* x_interface_info = "xilinx.com:interface:bram:1.0 BRAM_PORTB WE" *) input [0:0]web;
  (* x_interface_info = "xilinx.com:interface:bram:1.0 BRAM_PORTB ADDR" *) input [10:0]addrb;
  (* x_interface_info = "xilinx.com:interface:bram:1.0 BRAM_PORTB DIN" *) input [15:0]dinb;
  (* x_interface_info = "xilinx.com:interface:bram:1.0 BRAM_PORTB DOUT" *) output [15:0]doutb;

  wire [10:0]addra;
  wire [10:0]addrb;
  wire clka;
  wire [15:0]dina;
  wire [15:0]dinb;
  wire [15:0]douta;
  wire [15:0]doutb;
  wire [0:0]wea;
  wire [0:0]web;
  wire NLW_U0_dbiterr_UNCONNECTED;
  wire NLW_U0_rsta_busy_UNCONNECTED;
  wire NLW_U0_rstb_busy_UNCONNECTED;
  wire NLW_U0_s_axi_arready_UNCONNECTED;
  wire NLW_U0_s_axi_awready_UNCONNECTED;
  wire NLW_U0_s_axi_bvalid_UNCONNECTED;
  wire NLW_U0_s_axi_dbiterr_UNCONNECTED;
  wire NLW_U0_s_axi_rlast_UNCONNECTED;
  wire NLW_U0_s_axi_rvalid_UNCONNECTED;
  wire NLW_U0_s_axi_sbiterr_UNCONNECTED;
  wire NLW_U0_s_axi_wready_UNCONNECTED;
  wire NLW_U0_sbiterr_UNCONNECTED;
  wire [10:0]NLW_U0_rdaddrecc_UNCONNECTED;
  wire [3:0]NLW_U0_s_axi_bid_UNCONNECTED;
  wire [1:0]NLW_U0_s_axi_bresp_UNCONNECTED;
  wire [10:0]NLW_U0_s_axi_rdaddrecc_UNCONNECTED;
  wire [15:0]NLW_U0_s_axi_rdata_UNCONNECTED;
  wire [3:0]NLW_U0_s_axi_rid_UNCONNECTED;
  wire [1:0]NLW_U0_s_axi_rresp_UNCONNECTED;

  (* C_ADDRA_WIDTH = "11" *) 
  (* C_ADDRB_WIDTH = "11" *) 
  (* C_ALGORITHM = "1" *) 
  (* C_AXI_ID_WIDTH = "4" *) 
  (* C_AXI_SLAVE_TYPE = "0" *) 
  (* C_AXI_TYPE = "1" *) 
  (* C_BYTE_SIZE = "9" *) 
  (* C_COMMON_CLK = "1" *) 
  (* C_COUNT_18K_BRAM = "0" *) 
  (* C_COUNT_36K_BRAM = "1" *) 
  (* C_CTRL_ECC_ALGO = "NONE" *) 
  (* C_DEFAULT_DATA = "0" *) 
  (* C_DISABLE_WARN_BHV_COLL = "0" *) 
  (* C_DISABLE_WARN_BHV_RANGE = "0" *) 
  (* C_ELABORATION_DIR = "./" *) 
  (* C_ENABLE_32BIT_ADDRESS = "0" *) 
  (* C_EN_DEEPSLEEP_PIN = "0" *) 
  (* C_EN_ECC_PIPE = "0" *) 
  (* C_EN_RDADDRA_CHG = "0" *) 
  (* C_EN_RDADDRB_CHG = "0" *) 
  (* C_EN_SAFETY_CKT = "0" *) 
  (* C_EN_SHUTDOWN_PIN = "0" *) 
  (* C_EN_SLEEP_PIN = "0" *) 
  (* C_EST_POWER_SUMMARY = "Estimated Power for IP     :     5.349 mW" *) 
  (* C_FAMILY = "spartan7" *) 
  (* C_HAS_AXI_ID = "0" *) 
  (* C_HAS_ENA = "0" *) 
  (* C_HAS_ENB = "0" *) 
  (* C_HAS_INJECTERR = "0" *) 
  (* C_HAS_MEM_OUTPUT_REGS_A = "0" *) 
  (* C_HAS_MEM_OUTPUT_REGS_B = "0" *) 
  (* C_HAS_MUX_OUTPUT_REGS_A = "0" *) 
  (* C_HAS_MUX_OUTPUT_REGS_B = "0" *) 
  (* C_HAS_REGCEA = "0" *) 
  (* C_HAS_REGCEB = "0" *) 
  (* C_HAS_RSTA = "0" *) 
  (* C_HAS_RSTB = "0" *) 
  (* C_HAS_SOFTECC_INPUT_REGS_A = "0" *) 
  (* C_HAS_SOFTECC_OUTPUT_REGS_B = "0" *) 
  (* C_INITA_VAL = "0" *) 
  (* C_INITB_VAL = "0" *) 
  (* C_INIT_FILE = "j1_memory_4k.mem" *) 
  (* C_INIT_FILE_NAME = "j1_memory_4k.mif" *) 
  (* C_INTERFACE_TYPE = "0" *) 
  (* C_LOAD_INIT_FILE = "1" *) 
  (* C_MEM_TYPE = "2" *) 
  (* C_MUX_PIPELINE_STAGES = "0" *) 
  (* C_PRIM_TYPE = "1" *) 
  (* C_READ_DEPTH_A = "2048" *) 
  (* C_READ_DEPTH_B = "2048" *) 
  (* C_READ_LATENCY_A = "1" *) 
  (* C_READ_LATENCY_B = "1" *) 
  (* C_READ_WIDTH_A = "16" *) 
  (* C_READ_WIDTH_B = "16" *) 
  (* C_RSTRAM_A = "0" *) 
  (* C_RSTRAM_B = "0" *) 
  (* C_RST_PRIORITY_A = "CE" *) 
  (* C_RST_PRIORITY_B = "CE" *) 
  (* C_SIM_COLLISION_CHECK = "ALL" *) 
  (* C_USE_BRAM_BLOCK = "0" *) 
  (* C_USE_BYTE_WEA = "0" *) 
  (* C_USE_BYTE_WEB = "0" *) 
  (* C_USE_DEFAULT_DATA = "0" *) 
  (* C_USE_ECC = "0" *) 
  (* C_USE_SOFTECC = "0" *) 
  (* C_USE_URAM = "0" *) 
  (* C_WEA_WIDTH = "1" *) 
  (* C_WEB_WIDTH = "1" *) 
  (* C_WRITE_DEPTH_A = "2048" *) 
  (* C_WRITE_DEPTH_B = "2048" *) 
  (* C_WRITE_MODE_A = "WRITE_FIRST" *) 
  (* C_WRITE_MODE_B = "WRITE_FIRST" *) 
  (* C_WRITE_WIDTH_A = "16" *) 
  (* C_WRITE_WIDTH_B = "16" *) 
  (* C_XDEVICEFAMILY = "spartan7" *) 
  (* downgradeipidentifiedwarnings = "yes" *) 
  (* is_du_within_envelope = "true" *) 
  j1_memory_4k_blk_mem_gen_v8_4_10 U0
       (.addra(addra),
        .addrb(addrb),
        .clka(clka),
        .clkb(1'b0),
        .dbiterr(NLW_U0_dbiterr_UNCONNECTED),
        .deepsleep(1'b0),
        .dina(dina),
        .dinb(dinb),
        .douta(douta),
        .doutb(doutb),
        .eccpipece(1'b0),
        .ena(1'b0),
        .enb(1'b0),
        .injectdbiterr(1'b0),
        .injectsbiterr(1'b0),
        .rdaddrecc(NLW_U0_rdaddrecc_UNCONNECTED[10:0]),
        .regcea(1'b1),
        .regceb(1'b1),
        .rsta(1'b0),
        .rsta_busy(NLW_U0_rsta_busy_UNCONNECTED),
        .rstb(1'b0),
        .rstb_busy(NLW_U0_rstb_busy_UNCONNECTED),
        .s_aclk(1'b0),
        .s_aresetn(1'b0),
        .s_axi_araddr({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .s_axi_arburst({1'b0,1'b0}),
        .s_axi_arid({1'b0,1'b0,1'b0,1'b0}),
        .s_axi_arlen({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .s_axi_arready(NLW_U0_s_axi_arready_UNCONNECTED),
        .s_axi_arsize({1'b0,1'b0,1'b0}),
        .s_axi_arvalid(1'b0),
        .s_axi_awaddr({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .s_axi_awburst({1'b0,1'b0}),
        .s_axi_awid({1'b0,1'b0,1'b0,1'b0}),
        .s_axi_awlen({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .s_axi_awready(NLW_U0_s_axi_awready_UNCONNECTED),
        .s_axi_awsize({1'b0,1'b0,1'b0}),
        .s_axi_awvalid(1'b0),
        .s_axi_bid(NLW_U0_s_axi_bid_UNCONNECTED[3:0]),
        .s_axi_bready(1'b0),
        .s_axi_bresp(NLW_U0_s_axi_bresp_UNCONNECTED[1:0]),
        .s_axi_bvalid(NLW_U0_s_axi_bvalid_UNCONNECTED),
        .s_axi_dbiterr(NLW_U0_s_axi_dbiterr_UNCONNECTED),
        .s_axi_injectdbiterr(1'b0),
        .s_axi_injectsbiterr(1'b0),
        .s_axi_rdaddrecc(NLW_U0_s_axi_rdaddrecc_UNCONNECTED[10:0]),
        .s_axi_rdata(NLW_U0_s_axi_rdata_UNCONNECTED[15:0]),
        .s_axi_rid(NLW_U0_s_axi_rid_UNCONNECTED[3:0]),
        .s_axi_rlast(NLW_U0_s_axi_rlast_UNCONNECTED),
        .s_axi_rready(1'b0),
        .s_axi_rresp(NLW_U0_s_axi_rresp_UNCONNECTED[1:0]),
        .s_axi_rvalid(NLW_U0_s_axi_rvalid_UNCONNECTED),
        .s_axi_sbiterr(NLW_U0_s_axi_sbiterr_UNCONNECTED),
        .s_axi_wdata({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .s_axi_wlast(1'b0),
        .s_axi_wready(NLW_U0_s_axi_wready_UNCONNECTED),
        .s_axi_wstrb(1'b0),
        .s_axi_wvalid(1'b0),
        .sbiterr(NLW_U0_sbiterr_UNCONNECTED),
        .shutdown(1'b0),
        .sleep(1'b0),
        .wea(wea),
        .web(web));
endmodule
`pragma protect begin_protected
`pragma protect version = 1
`pragma protect encrypt_agent = "XILINX"
`pragma protect encrypt_agent_info = "Xilinx Encryption Tool 2024.2.1"
`pragma protect key_keyowner="Synopsys", key_keyname="SNPS-VCS-RSA-2", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`pragma protect key_block
udNP8Uje7hpcvCYAXvDW9r2oHQyRipDN507b+1w27rP7xb4Nz9QLRyKQf6hKRcDEOVPPDU4KvXyQ
S7Bed2F6O4Ldaml88+U6QsrNFaZ4fNsTrKjEE3lLix8fjqIyUXKSNeepsabnRAwnPTjGP0ckeQ0z
/6vK6vS6Oh2J5EcQEag=

`pragma protect key_keyowner="Aldec", key_keyname="ALDEC15_001", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
AJCFEJ1YmO8l6c55nmqjPHpq03iIwIWhcq4gzpGTG9q8+B6G84WceO3Y0MOwVkIC+rza8yWW4W96
aueSQ6zP9DeJpaQAa5CXah55dY7AxCSywtOyZ62CZYm1RxvTaNigNnppCye+yAHN5Qei2IV4ZMwt
hFhXp7bbKeSQsqyTcPao+XMOfUQgs6uHRQoMvRFgoHByuZ20V72oOw3MoBmzaFgyRicvku2AVEWd
uJDCqcRlHIZZ1c+O+dCjOvRg+9aaQ1DE8gyCtne0FhQEvVnAPjcTzeUg2I0bZrpUQbbS8p5716Jl
/R7teOvv2VpnKxyFvW5lTVImrqIsvdk38CH5aw==

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VELOCE-RSA", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`pragma protect key_block
d1PZzLTrVgGa7lAGrEOnBHSkyRph92ENzEYYfBv5ShW44EZ/4/Dy5IpHq0athhXF90+7+EiPDjze
BIUrzaCZjSn3hPfQYuPqbUjXLseT1xBYmtHZtyzpQYUr38hRTWh6IjNX2anC6vrScheJp7oDyY1/
IpdhxPVK/6z5GGw/+fk=

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VERIF-SIM-RSA-2", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
iXAE+ZmeGhifmLMp5oEFkhP/d/cDFVKwwxydC1lMN6LBRLFXElE5VcBvIEPtGNusskpxv/GPCPge
Az6W1/YbULAD2vlMA71EljrnHet4zg4sh561cjLPQN2DUNHr/8qxlo4ONww5HrNW+aj3zt0V9iXd
LMCR8NG58iQqMP1t5ybi/4urLnu1EF4AFJP8eDrIn+UhiFljJ04qUkg6UteUS1Qbzshw6awFUiey
WBeovfV6FXCJKwHugmJ9lX0v8OpeazDBCdnLiduAGRdSYyvX8gZsv3vJDGtRy/jgipU3YvWtjuVV
YtKThRWW0HDHoUbtraCor3GB7nSBYetgLBhI2w==

`pragma protect key_keyowner="Real Intent", key_keyname="RI-RSA-KEY-1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
CCwrvinvzJ/ig55I5/d/Amnn8e78wAQQ3CZeQChsQV8lNb/2YZzJQqDeIZnIw2PW9XMMQWu1BZ8c
iNYcwzM1UFZoOaZeVnYUYwb2RIF29CtoBJrR/IdRvyNiLiX6yB25jHmLHr0ZI2+HcOU/DUGMCHdj
rXeeb/zWm2+BlGVXo8nZQsBLb7Ax2MZrkpa0MTARS71LcKF7w1t4GoY7bVE/6IqiapBrM+ZEG0G0
A/Ha5M7b0iGDPUjoi9W9dI+/QCxu2Jzm/2Lv/GivvO91GfWy+GtP+BOuITXoh1RMI1r+C0BVFEmZ
cJTPz6NO//KkkLFG9/hmPYFN1LfA2Ba990gqjw==

`pragma protect key_keyowner="Xilinx", key_keyname="xilinxt_2023_11", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
UtpgxYdpPKuSNM+KxM6Sv3Iy4ZOFYPNHS2XNuKmMlCw2QC5U4+i3rdVze9p+UBDrx6Er9G9pm8c7
cuUkBFDSwAo1nmCsTUQkSQOtPXr5uH5HznaUeoa9jW2AL4fdOIyDGx9ybjy86RZqbLwFXSFl5h+u
N7pnU5jSiJzRe2r8HEgZz2gz/hfTN/jzQXetqGKueHxsQ3aoufearKsdAddLj5L+S7JaV0vI1A+I
C0NrqJNr80rSabETlIhyDi8M+O31ACijPvd5lxs/aM4t0hkDuJEjD/4zSMAR4kX6rFuoAaGj+gkL
JNO4LonSwyx9V/aLCUGZvakCGOoTfa8HsXALSg==

`pragma protect key_keyowner="Metrics Technologies Inc.", key_keyname="DSim", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
bYpkb72jOpiSeCQ5PRip31Y2zumke9hnzyF2MW+IVzPW0m3jVUMoEwgSxAqE+vlQuzZiaESSLPa4
hEofuBzsD/1HhUexhJNB4Y+/VPBvwWtiuiJJBrLU2aBqlxKZznTLdxMXRPgndyi9c3Bm+BaDdRxt
QobwAkJhk6Cy+jZEy/kc8piXqUSO6chEDW5OWt1z8Yp5BR7KL5Wbm2MilK8JLKlm/z19oTOcUu4h
Zc/O6xJcNdqjekuqJ6hg7HEz9U1UKFQudRtsv7J0+tBPchAGiv5TypyI+/t+vNPdEWYYqMpLIvZN
cCSJD0PTRiRj5gWzhCtfKhiGSqaSGSjo2ySroQ==

`pragma protect key_keyowner="Atrenta", key_keyname="ATR-SG-RSA-1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=384)
`pragma protect key_block
sHfsIbA/GTiYiIhFVT+ta4MYPEvZVn5bzP0L9SmLFYXxtXCWmeDpCp9ZZwtGS9IH6xlOR9TtFG5W
pgKkFb5r5QCZfajiTmrZfPjhvh247eO53zGpnNOd0OD8ieVYpE+zrABiidJQZIJKyypvLU+yKMcK
ieY1rJH9psSNTXb3F5RJBwS7BAIUABNBZQnGq7oy4LEOxgBNofWAIW356JOU+bZ9yTI94wEStpim
5BFs8fstAwWnwM6ZBxHDgmukn8PzlJVxzDFileHS+GIb5lPZJAMfhj/nCnvFAKrsVpYMjDZiwUXS
inHd4rP1QfU6bBAS5qhsBh1LbedSjDIbguzLNaMGqf3V74evgzM0Ps8jg9qHcPLyqUD36zjCw262
gOC0ofer0rkLqaM6oyYN9vLgtccUgx1yvJlD41DPYJxSSgHkRG/5QSwS1sPS1s3Akwg0CFWU6kDJ
IgTusnQGjwO0kd7isRhV5vbprQccIjmYDSkUVuuQ1QKIJdSZNgqBKujv

`pragma protect key_keyowner="Cadence Design Systems.", key_keyname="CDS_RSA_KEY_VER_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
ni0skYr41xEhGcERgtNsJJ63OdYzP9ki5X7c3IbnsFCvWxeRQKlubX6N8A/0jpNXOv7aZEKafLZ1
qwbSeUvbN5EGxOtmP500LKoc6ooFVOT30GABYPyplJZQKkOV1gCLsFgwAOvKXk0nzR3DidZfgNmV
WzVuzpauwrR4E5VbDQ5MRanHIv9fUJyWGO5b0vBraafqmyDaWmLnOjDZvy2FLKT8h/g+leYjmoOW
ZJ6PXCZ0Q4ga21Xt6erSGIYPOkEEG6WbpWPjflxT9mjFpLmFZ9GiIu/sAP35ujidUd4QOQ1OhsD2
xotuK4Bk3godsqXIIt4XQ32YzMS3QWkODMZ9tQ==

`pragma protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
Vr9cGi332/lxwY+1s1c/q/QC1iXTtfGX0cX5Ee8iMu9RcXLuTLEJUJMfxD3nNqpTzZPP2uje9SLL
ag4NXGXSpax2KTl6n0ZR19GRYIQeoyuIEObQQuuUjIKIJWfhtOUJl3OTHWIfOKbakya+nCm5WfDr
xgAKiWZOPd4QTtzIfurdl1JtQQHX8Df2qJz7sQ85KbEnr9f0x0Z/P+vOiNCy0ZYtVnvaUhSssVFw
l2tWmTqvL+Cqw0ceq0VyZ+3vpLw66QGWxVHdhMsrsyfNGyr3ihgnG3a7Y1MCMfOZq/SVFUt69F0M
XHyhnqbPQtcHQDzO9skrKwKEzN4uFs0H5KYx8A==

`pragma protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-PREC-RSA", key_method="rsa"
`pragma protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`pragma protect key_block
VzSc8XP1P8vnrcckgvVZGDZrGVT26w6xIjvo6a/h45CvlV+9LQYT27zdvXxkL5tmT5FePC9paUrR
foCdInU0kmlUZ759cK2VrUmeyxKT8HXWg6xlTw+mzpcVQ2L5RccoD+x7DUGD5oYrTIKMHhEjKj2t
V5hsm6x8SS58U2hgBj9Mrc9VsyQ5ckv5iHJPaptGNowNckVd/hBogWZomkIxlcUdE/M9DVvqxhVz
Tt6fy92B4AgzzJMfxezRMyx9/CEBICI15TibBxghqNpC23LHFun7+S3oDsoVwo9MdfJEo7qaiix2
uWtEvbP+An3VxhS+5G3uf+JyDLZlNZjjujiAuQ==

`pragma protect data_method = "AES128-CBC"
`pragma protect encoding = (enctype = "BASE64", line_length = 76, bytes = 28032)
`pragma protect data_block
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
`pragma protect end_protected
`ifndef GLBL
`define GLBL
`timescale  1 ps / 1 ps

module glbl ();

    parameter ROC_WIDTH = 100000;
    parameter TOC_WIDTH = 0;
    parameter GRES_WIDTH = 10000;
    parameter GRES_START = 10000;

//--------   STARTUP Globals --------------
    wire GSR;
    wire GTS;
    wire GWE;
    wire PRLD;
    wire GRESTORE;
    tri1 p_up_tmp;
    tri (weak1, strong0) PLL_LOCKG = p_up_tmp;

    wire PROGB_GLBL;
    wire CCLKO_GLBL;
    wire FCSBO_GLBL;
    wire [3:0] DO_GLBL;
    wire [3:0] DI_GLBL;
   
    reg GSR_int;
    reg GTS_int;
    reg PRLD_int;
    reg GRESTORE_int;

//--------   JTAG Globals --------------
    wire JTAG_TDO_GLBL;
    wire JTAG_TCK_GLBL;
    wire JTAG_TDI_GLBL;
    wire JTAG_TMS_GLBL;
    wire JTAG_TRST_GLBL;

    reg JTAG_CAPTURE_GLBL;
    reg JTAG_RESET_GLBL;
    reg JTAG_SHIFT_GLBL;
    reg JTAG_UPDATE_GLBL;
    reg JTAG_RUNTEST_GLBL;

    reg JTAG_SEL1_GLBL = 0;
    reg JTAG_SEL2_GLBL = 0 ;
    reg JTAG_SEL3_GLBL = 0;
    reg JTAG_SEL4_GLBL = 0;

    reg JTAG_USER_TDO1_GLBL = 1'bz;
    reg JTAG_USER_TDO2_GLBL = 1'bz;
    reg JTAG_USER_TDO3_GLBL = 1'bz;
    reg JTAG_USER_TDO4_GLBL = 1'bz;

    assign (strong1, weak0) GSR = GSR_int;
    assign (strong1, weak0) GTS = GTS_int;
    assign (weak1, weak0) PRLD = PRLD_int;
    assign (strong1, weak0) GRESTORE = GRESTORE_int;

    initial begin
	GSR_int = 1'b1;
	PRLD_int = 1'b1;
	#(ROC_WIDTH)
	GSR_int = 1'b0;
	PRLD_int = 1'b0;
    end

    initial begin
	GTS_int = 1'b1;
	#(TOC_WIDTH)
	GTS_int = 1'b0;
    end

    initial begin 
	GRESTORE_int = 1'b0;
	#(GRES_START);
	GRESTORE_int = 1'b1;
	#(GRES_WIDTH);
	GRESTORE_int = 1'b0;
    end

endmodule
`endif
