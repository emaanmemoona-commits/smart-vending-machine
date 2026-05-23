`timescale 1ns / 1ps

module vending_machine_tb;

    // Inputs
    reg clk;
    reg rst_n;
    reg X;
    reg Y;
    reg C;

    // Outputs
    wire D;
    wire R;
    wire [1:0] current_state;

    // Instantiate the Unit Under Test (UUT)
    vending_machine uut (
        .clk(clk),
        .rst_n(rst_n),
        .X(X),
        .Y(Y),
        .C(C),
        .D(D),
        .R(R),
        .current_state(current_state)
    );

    // Clock Generation (Toggle every 5ns -> 10ns period)
    always #5 clk = ~clk;

    initial begin
        // Initialize Inputs
        clk = 0;
        rst_n = 0;
        X = 0;
        Y = 0;
        C = 0;

        // Apply Reset
        #10 rst_n = 1;
        
        // --- TEST CASE 1: Path A (Insert Rs. 10 then Rs. 5) ---
        #10 Y = 1; // Insert Rs. 10
        #10 Y = 0; // Unhold input after clock edge updates state to S2
        
        #10 X = 1; // Insert Rs. 5 (Mealy output D should instantly hit 1 here)
        #10 X = 0; // Unhold input after state resets to S0
        
        // --- TEST CASE 2: Overpay Condition (Insert Rs. 10 then Rs. 10) ---
        #20 Y = 1; // Insert Rs. 10 -> Moves to S2
        #10 Y = 0; 
        
        #10 Y = 1; // Insert second Rs. 10 (Outputs D and R should both hit 1)
        #10 Y = 0;

        // --- TEST CASE 3: Cancel Transaction ---
        #20 X = 1; // Insert Rs. 5 -> Moves to S1
        #10 X = 0;
        #10 C = 1; // Press Cancel -> Output R hits 1, returns to S0
        #10 C = 0;

        #20 $finish;
    end
    
endmodule