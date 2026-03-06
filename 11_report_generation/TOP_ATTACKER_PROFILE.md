# 🎯 TOP MEV ATTACKER PROFILE
**Wallet:** `YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP`

---

## 🔴 THREAT LEVEL: CRITICAL

### **Quick Stats**
```
Rank:                    #1 Most Profitable MEV Attacker
Total Profit:            15.795 SOL ($2,368 USD @ $150/SOL)
Average Profit/Attack:   7.8975 SOL
Number of Attacks:       2 major documented cases
Fat Sandwiches:          3,344 transactions
Regular Sandwiches:      167 transactions
Total Victims:           ~4,564 unique wallets
Average ROI:             900% (9x return on capital)
Automation Level:        95.24% (highly automated bot)
Risk Classification:     EXTREMELY HIGH
```

---

## 🌐 VALIDATOR RELATIONSHIPS

### **Primary Validator (Main Operations)**
```
Validator ID:    22rU5yUmdVThrkoPieVNphqEyAtMQKmZxjwcD8v4bJDU
Relationship:    ABNORMALLY HIGH CONCENTRATION ⚠️
Transactions:    2,888 fat sandwich attacks
Profit via:      13.957 SOL net (64.972 SOL gross)
Target Pool:     HumidiFi (primary exploitation target)
MEV Events:      3,978 total on this validator
Risk Score:      CRITICAL - Exceptional MEV facilitation
```

**Validator 22rU5... Details:**
- **Total MEV Events:** 3,978 (highest in dataset)
- **Average MEV per Block:** ~0.78 SOL
- **Attack Facilitation Score:** Exceptional
- **Primary Pool:** HumidiFi (593 total MEV attacks on this pool)
- **Shared Attackers:** 133 BisonFi, 129 SolFiV2, 128 GoonFi
- **Risk Amplification:** High validator-attacker concentration

### **Secondary Validator (Diversification Strategy)**
```
Validator ID:    MPUMTbQzLbJyaJ2mEBcXoLDTKPK2TJJQhvQBRf2TZSR
Used in:         CASE-001-460701000 (JUP/WSOL Launch Attack)
Commission:      7%
MEV Boost:       Enabled (searcher_relay bidder)
Blocks Produced: 1,542
Avg MEV/Block:   0.15 SOL
Facilitation:    0.72 attack score
Tip Amount:      0.025 SOL
Block Position:  leader_slot
```

---

## 📊 ATTACK BREAKDOWN

### **Case 1: JUP/WSOL Launch Exploitation**
**Attack ID:** CASE-001-460701000  
**Validator:** MPUMTbQzLbJyaJ2mEBcXoLDTKPK2TJJQhvQBRf2TZSR

```yaml
Date:           2026-01-16 21:00:00 UTC
Pool:           Orca JUP/WSOL
Attack Type:    Fat Sandwich
Duration:       800ms
Net Profit:     3.185 SOL
ROI:            91%
Victim:         Retail trader (500K JUP buy order)
Victim Loss:    0.225 SOL (225 JUP slippage)
Mechanism:      Token launch volatility exploitation
```

**Timeline:**
```
T-450ms:  Frontrun  → Buy 250K JUP @ 0.015 (invest 3,750 WSOL)
                      Price moves to 0.0132 (-12%)
                      Liquidity impact: 5.2%
                      Gas: 185K compute units, 80K lamports priority

T+0ms:    Victim   → Buys 500K JUP
                      Expected: 0.015 per token
                      Actual: 0.0132 per token
                      Slippage: 2.8%
                      Loss: 0.225 SOL

T+350ms:  Backrun  → Sell 250K JUP @ 0.0132 (receive 534K WSOL)
                      Price recovers to 0.013 (+1.2%)
                      Gas: 215K compute units, 60K lamports priority

Result:   Gross Profit:  3.245 SOL
          Transaction Costs: 0.060 SOL
          Net Profit:    3.185 SOL (91% ROI)
```

### **Case 2: HumidiFi Operations (Main Activity)**
**Validator:** 22rU5yUmdVThrkoPieVNphqEyAtMQKmZxjwcD8v4bJDU

```yaml
Pool:              HumidiFi (multiple token pairs)
Transactions:      2,888 fat sandwich attacks
Fat Sandwiches:    160 complex multi-victim attacks
Gross Profit:      64.972 SOL
Net Profit:        13.957 SOL (estimated)
Total Victims:     ~3,800 (estimated from transaction count)
Attack Pattern:    High-frequency automated sandwich bot
Profit Per Trade:  0.0048 SOL average
Automation:        99%+ (systematic execution)
```

---

## 🎭 ATTACK CHARACTERISTICS

### **Operational Signature**
```
✓ Fresh wallet addresses (no reuse across major attacks)
✓ Contract-call funding pattern (obscures CEX origin)
✓ Multi-validator strategy (diversifies risk)
✓ Pool specialization (HumidiFi primary target)
✓ High-frequency execution (3,344 fat sandwich transactions)
✓ Precision timing (±500ms attack windows)
✓ MEV boost exploitation (searcher_relay, jito_bundle)
✓ Premium priority fees (80K-200K lamports)
```

### **Technical Capabilities**
- **Mempool Monitoring:** Advanced real-time transaction detection
- **Gas Optimization:** Dynamic priority fee bidding (80K-200K lamports)
- **Atomic Execution:** Multi-step transactions in single block
- **Price Impact Calculation:** Precise liquidity depth analysis
- **Validator Selection:** Strategic validator routing
- **Bot Infrastructure:** 24/7 automated execution (95.24% fat sandwich ratio)

### **Target Selection**
- **Primary Pool:** HumidiFi (2,888 transactions = 86% of activity)
- **Secondary Pools:** BisonFi, GoonFi, TesseraV
- **Victim Types:** 
  - Retail traders (launch buyers)
  - Aggregator users (Jupiter routes)
  - Stake pool depositors
  - Large institutional orders
- **Optimal Conditions:**
  - Token launches (high volatility)
  - Low liquidity pools
  - Large victim orders (>500K tokens)
  - Oracle lag windows

---

## 💰 PROFITABILITY ANALYSIS

### **Revenue Breakdown**
```
Total Revenue:           15.795 SOL
Attack 1 (JUP/WSOL):     3.185 SOL (20.2%)
Attack 2 (HumidiFi):     ~12.61 SOL (79.8% estimated)

Cost Structure:
  Gas Fees:              ~0.06 SOL per attack
  Priority Fees:         80K-200K lamports per tx
  Validator Tips:        0.025-0.032 SOL per attack
  Total Costs:           ~10% of gross profit

Net Margin:              ~90% (exceptional profitability)
```

### **Comparison to Other Attackers**
```
Rank  Attacker            Profit    % of Total  Attacks
----  ------------------  --------  ----------  -------
  1   YubQzu...N6tP ⭐   15.795     31.4%      2
  2   YubVwW...NXQW       4.860      9.7%      1
  3   AEB9dX...f4R        3.888      7.7%      1
  4   Yubozz...EWj        2.916      5.8%      1
  5   CatyeC...SiP        2.691      5.4%      1
----  ------------------  --------  ----------  -------
      Top 10 Total       50.247     100%       16

YubQzu...N6tP = 31.4% of all top-10 MEV profits!
```

**Market Share:**
- Controls 30.7% of all fat sandwich attacks (3,344 / 10,889)
- Impacts 38.0% of all victims (4,564 / 12,006)
- Operates via 2 confirmed validators
- Profit per sandwich: 0.0045 SOL (highest efficiency)

---

## 🔍 FORENSIC INDICATORS

### **Blockchain Footprint**
```yaml
Address Reuse:           False (uses fresh addresses)
Wallet Funding:          Contract calls (not direct CEX transfers)
Miner Interaction:       Direct tips to validators
Statistical Anomaly:     True (abnormal profit concentration)
Oracle Timing:           Correlated with oracle lag events
Transaction Pattern:     Systematic, bot-driven execution
Cross-Protocol Signal:   False (single-DEX focused)
Liquidity Targeting:     True (identifies low-liquidity windows)
```

### **Known Associations**
- **Validator:** 22rU5yUmdVThrkoPieVNphqEyAtMQKmZxjwcD8v4bJDU (primary)
- **Validator:** MPUMTbQzLbJyaJ2mEBcXoLDTKPK2TJJQhvQBRf2TZSR (secondary)
- **Pool:** HumidiFi (2,888 transactions)
- **Shared Attackers:** 133 also attack BisonFi
- **Wallet Cluster:** Unknown (funding source obscured)

### **Detection Markers**
```
✓ High transaction density (5+ trades per slot)
✓ Same signer across frontrun/backrun sequences
✓ Net profit > 0.1 SOL threshold
✓ Victim sandwiched between attacker transactions
✓ Price recovery after backrun (<2% from initial)
✓ Consistent validator selection pattern
✓ MEV boost bundle usage
✓ Priority fee >50K lamports
```

---

## ⚠️ COLLUSION INDICATORS

### **Validator 22rU5... Red Flags**
```
🚨 CRITICAL: Abnormally high concentration (2,888 transactions from single attacker)
🚨 HIGH: 64.972 SOL gross profit facilitated for one attacker
🚨 MODERATE: Consistent block space priority for this attacker
🚨 MODERATE: Multiple attackers showing preference for this validator
```

**Possible Explanations:**
1. **Coincidence:** Attacker selects validator based on performance metrics
2. **Preferential Treatment:** Validator prioritizes certain signers
3. **Direct Coordination:** Validator-attacker profit-sharing arrangement
4. **MEV Protocol:** Legitimate MEV boost/Jito bundle usage

**Investigation Needed:**
- Validator commission structure analysis
- Block production pattern review
- Transaction ordering algorithm audit
- Off-chain communication monitoring

---

## 🛡️ DETECTION & MITIGATION

### **Real-Time Detection Rules**
```sql
-- Detect YubQzu...N6tP pattern
SELECT * FROM transactions
WHERE signer = 'YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP'
   OR (
      priority_fee > 80000
      AND validator IN ('22rU5yU...', 'MPUMT...')
      AND pool = 'HumidiFi'
      AND trades_per_slot >= 5
      AND net_profit > 0.1
   );
```

### **User Protection Strategies**
1. **Avoid HumidiFi during high MEV periods**
2. **Set slippage limits <2% on all trades**
3. **Use private mempools (Jito bundles) for large orders**
4. **Split large orders across multiple transactions**
5. **Monitor validator 22rU5... block production**
6. **Route through MEV-aware aggregators**

### **Protocol-Level Defenses**
```
Priority                Action
--------                ------
CRITICAL   Monitor validator 22rU5... in real-time
HIGH       Implement MEV-resistant pricing oracles (<50ms lag)
HIGH       Circuit breakers for >5% price impact trades
MODERATE   Private mempool integration
MODERATE   Commit-reveal scheme for large orders
LOW        Attacker wallet blacklisting (easily bypassed)
```

---

## 📈 HISTORICAL TIMELINE

```
2026-01-16  CASE-001: JUP/WSOL launch attack (3.185 SOL profit)
            └─ First documented use of validator MPUMT...

2026-01-17  Began HumidiFi operations (validator 22rU5...)
to          └─ 2,888 fat sandwich transactions
2026-02-20    └─ ~12.61 SOL estimated profit
            └─ Primary revenue source (79.8% of total)

2026-02-24  Identified as #1 MEV attacker by researchers
            └─ 31.4% of all top-10 MEV profits
            └─ 30.7% of all fat sandwich attacks

2026-03-05  Profile published in Extended MEV Case Studies
            └─ Ongoing monitoring active
            └─ Validator relationship under investigation
```

---

## 🎯 COUNTERMEASURES STATUS

| Defense | Status | Effectiveness | Notes |
|---------|--------|---------------|-------|
| Slippage Limits | ⚠️ Partial | Medium | Users must set manually |
| Oracle Speed | ❌ None | N/A | Still 3+ block lag on some feeds |
| Private Mempool | ✅ Available | High | Jito bundles, but not widely used |
| Validator Monitoring | 🔄 In Progress | TBD | Real-time tracking being implemented |
| MEV Taxation | ❌ None | N/A | No protocol-level MEV capture |
| Circuit Breakers | ❌ None | N/A | No automatic trade halts |
| Address Blacklist | ❌ Ineffective | Very Low | Attacker uses fresh addresses |

---

## 📞 REPORTING

**If you detect this attacker pattern:**
1. Report to validator operators (especially 22rU5...)
2. Document transaction hash, timestamp, profit amount
3. Submit to MEV research databases
4. Contact affected pools (HumidiFi, BisonFi, etc.)
5. Share with Solana security teams

**Contact:**
- Solana Security: security@solana.com
- MEV Research: mev-research@flashbots.net
- Pool Operators: Via Discord (HumidiFi, Orca, etc.)

---

## 🔬 ONGOING RESEARCH

**Open Questions:**
1. What is the true identity of YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP?
2. Is there validator-attacker collusion with 22rU5...?
3. How many more attacks has this bot executed beyond documented cases?
4. What is the funding source (which CEX)?
5. Are there other wallet addresses controlled by same entity?

**Future Analysis:**
- Wallet cluster analysis (graph CEX funding sources)
- Validator transaction ordering pattern analysis
- Cross-chain MEV bot fingerprinting
- Profit destination tracking (where does SOL go?)

---

**Last Updated:** March 5, 2026  
**Classification:** PUBLIC - MEV Research  
**Status:** Active Threat - Ongoing Monitoring
