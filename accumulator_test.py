import math

def calculate_accumulated_slip_risk(selected_bet_lines):
    print("📱 FC Engine: Compounding Bet Slip Risks...")
    print("------------------------------------------------")
    
    total_implied_odds = 1.0
    compounded_probability = 1.0
    
    # Loop through every selection added to our phone drawer
    for idx, line in enumerate(selected_bet_lines, 1):
        market = line["market"]
        odds = line["odds"]
        
        # Convert the bookmaker's decimal price back into an exact probability percentage
        # e.g., 2.00 odds means a 50% implied chance (1 / 2.00)
        line_probability = 1.0 / odds
        
        # Compound the parameters
        total_implied_odds *= odds
        compounded_probability *= line_probability
        
        # Convert to a readable percentage format
        current_slip_pct = compounded_probability * 100
        
        # Assign an Apple-style risk tier string based on true probability thresholds
        if current_slip_pct > 45:
            risk_tier = "🟢 LOW RISK (Strong Core Likelihood)"
        elif current_slip_pct > 20:
            risk_tier = "🟡 MODERATE RISK (Frictional Edge)"
        elif current_slip_pct > 8:
            risk_tier = "🟠 HIGH RISK (Speculative Margin)"
        else:
            risk_tier = "🔴 EXTREME RISK (Volatile Accumulation)"
            
        print(f"Line {idx} Added: {market}")
        print(f"   * Individual Odds: {odds:.2f} (Implied Chance: {line_probability*100:.1f}%)")
        print(f"   * Slip Total Odds: {total_implied_odds:.2f}")
        print(f"   * True Slip Probability: {current_slip_pct:.2f}%")
        print(f"   * Status: {risk_tier}\n")
        
    print("------------------------------------------------")
    print(f"🏁 FINAL SELECTION COMPILATION:")
    print(f"   * Total Multi-Bet Return Price: {total_implied_odds:.2f}")
    print(f"   * Absolute Likelihood of Slip Hitting: {compounded_probability * 100:.2f}%")
    
    return total_implied_odds, compounded_probability

# =====================================================================
# RUN ACCUMULATOR SIMULATION ISOLATION TEST
# =====================================================================
if __name__ == "__main__":
    print("🚀 --- INITIALIZING FOOTBALL CORE (FC) SLIP ACCUMULATOR --- 🚀\n")
    
    # Simulate a user checking calculations on their iPhone app and adding 3 lines to their slip:
    # 1. Slavia Prague Win against Sparta Prague
    # 2. Arsenal vs Chelsea Match to go OVER 9.5 Corners
    # 3. Mexico vs South Africa Expected Total Cards to go OVER 3.5
    mock_iphone_bet_slip = [
        {"market": "Slavia Prague (Match Win)", "odds": 1.72},
        {"market": "Arsenal vs Chelsea (Over 9.5 Corners)", "odds": 1.85},
        {"market": "Mexico vs South Africa (Over 3.5 Total Cards)", "odds": 2.10}
    ]
    
    final_odds, final_prob = calculate_accumulated_slip_risk(mock_iphone_bet_slip)
    
    print("\n🏁 --- FC ACCUMULATOR RUN COMPLETE --- 🏁")
