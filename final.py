import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Multi-Agent RFP Intelligence System",
    layout="wide"
)

# =========================================================
# SESSION STATE INITIALIZATION (ONE-TIME RUN MODEL)
# =========================================================
if "system_ran" not in st.session_state:
    st.session_state.system_ran = False
    st.session_state.sales_out = None
    st.session_state.selected = None
    st.session_state.capacity_used = None
    st.session_state.run_timestamp = None

# =========================================================
# GLOBAL STYLES (DARK THEME SAFE)
# =========================================================
st.markdown("""
<style>
html, body, [class*="css"] { color: #EAEAEA !important; }

.main-title {
    font-size: 34px;
    font-weight: 700;
    color: #FFFFFF;
}
.sub-title {
    font-size: 16px;
    color: #B0B3B8;
    margin-bottom: 25px;
}

.section {
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 25px;
    border: 1px solid #2A2A2A;
}

.green-box { background: #0E2A1E; }
.amber-box { background: #2A240E; }
.blue-box  { background: #0E1A2A; }

.section h2, .section h3 { color: #FFFFFF !important; }

thead tr th {
    background-color: #1F2937 !important;
    color: #FFFFFF !important;
}
tbody tr td {
    color: #E5E7EB !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown("<div class='main-title'>Multi-Agent RFP Intelligence System</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>Agent-wise dashboards for RFP prioritization, technical feasibility, pricing, and bid decisions</div>",
    unsafe_allow_html=True
)

# =========================================================
# DATA
# =========================================================
today = datetime.today()

rfps = pd.DataFrame([
    {"RFP_ID": 1, "Buyer": "State Power PSU", "Due Date": today + timedelta(days=30),
     "Product": "220kV HT XLPE Cable", "Standards": ["IEC 60502", "IS 7098"], "Tests": ["Type", "Routine", "Acceptance"]},
    {"RFP_ID": 2, "Buyer": "Metro Rail Corporation", "Due Date": today + timedelta(days=65),
     "Product": "33kV HT Cable", "Standards": ["IEC 60502"], "Tests": ["Routine"]},
    {"RFP_ID": 3, "Buyer": "Steel Plant", "Due Date": today + timedelta(days=55),
     "Product": "LT Control Cable", "Standards": ["IS 694"], "Tests": ["Routine"]},
    {"RFP_ID": 4, "Buyer": "Transmission PSU", "Due Date": today + timedelta(days=80),
     "Product": "132kV HT XLPE Cable", "Standards": ["IEC 60502"], "Tests": ["Type", "Routine"]},
    {"RFP_ID": 5, "Buyer": "Solar Park Developer", "Due Date": today + timedelta(days=45),
     "Product": "33kV HT Cable", "Standards": ["IEC 60502"], "Tests": ["Routine"]},
    {"RFP_ID": 6, "Buyer": "Refinery Project", "Due Date": today + timedelta(days=70),
     "Product": "LT Control Cable", "Standards": ["IS 694"], "Tests": ["Routine"]},
    {"RFP_ID": 7, "Buyer": "Urban Infra Authority", "Due Date": today + timedelta(days=35),
     "Product": "132kV HT XLPE Cable", "Standards": ["IEC 60502"], "Tests": ["Type", "Routine"]},
    {"RFP_ID": 8, "Buyer": "Industrial EPC", "Due Date": today + timedelta(days=60),
     "Product": "220kV HT XLPE Cable", "Standards": ["IEC 60502", "IS 7098"], "Tests": ["Routine"]},
    {"RFP_ID": 9, "Buyer": "Airport Authority", "Due Date": today + timedelta(days=50),
     "Product": "33kV HT Cable", "Standards": ["IEC 60502"], "Tests": ["Routine"]},
    {"RFP_ID": 10, "Buyer": "IT Park Developer", "Due Date": today + timedelta(days=40),
     "Product": "Optical Fiber Cable", "Standards": ["IEC"], "Tests": ["Routine"]},
])

portfolio = [
    "220kV HT XLPE Cable",
    "132kV HT XLPE Cable",
    "33kV HT Cable",
    "LT Control Cable"
]

sku_data = pd.DataFrame([
    {"SKU_ID": 1, "SKU": "220kV-XLPE-CU", "Standards": ["IEC 60502", "IS 7098"]},
    {"SKU_ID": 2, "SKU": "220kV-XLPE-AL", "Standards": ["IEC 60502"]},
    {"SKU_ID": 3, "SKU": "132kV-XLPE-AL", "Standards": ["IEC 60502"]},
    {"SKU_ID": 4, "SKU": "33kV-XLPE-AL", "Standards": ["IEC 60502"]},
    {"SKU_ID": 5, "SKU": "LT-PVC-CU", "Standards": ["IS 694"]},
    {"SKU_ID": 6, "SKU": "LT-PVC-AL", "Standards": ["IS 694"]},
])

pricing_master = {1:120000, 2:110000, 3:80000, 4:45000, 5:15000, 6:12000}
test_costs = {"Type":500000, "Routine":50000, "Acceptance":200000}

# =========================================================
# AGENT FUNCTIONS
# =========================================================
def sales_agent():
    rows = []
    for _, r in rfps.iterrows():
        relevant = r["Product"] in portfolio
        days_left = (r["Due Date"] - today).days
        urgency = max(0, (90 - days_left) / 90)
        score = round(0.6 * urgency + 0.4 * relevant, 2)
        priority = "Discarded" if not relevant else "High" if score >= 0.75 else "Medium" if score >= 0.6 else "Low"
        rows.append({
            "RFP ID": r["RFP_ID"],
            "Buyer": r["Buyer"],
            "Product": r["Product"],
            "Due Date": r["Due Date"].date(),
            "Opportunity Score": score,
            "Priority": priority,
            "Relevant": relevant
        })
    return pd.DataFrame(rows).sort_values("Opportunity Score", ascending=False)

def technical_agent(rfp):
    if "220kV" in rfp["Product"]:
        req_voltage = "220kV"
    elif "132kV" in rfp["Product"]:
        req_voltage = "132kV"
    elif "33kV" in rfp["Product"]:
        req_voltage = "33kV"
    else:
        req_voltage = "LT"

    rows = []
    for _, sku in sku_data.iterrows():
        checks = {
            "Voltage": {"Match": sku["SKU"].startswith(req_voltage), "Critical": True},
            "Insulation": {"Match": True, "Critical": False},
            "Standards": {"Match": all(s in sku["Standards"] for s in rfp["Standards"]), "Critical": True},
            "Conductor": {"Match": True, "Critical": False},
        }

        match_pct = round(sum(v["Match"] for v in checks.values()) / len(checks) * 100, 1)

        deviations = []
        critical_fail = False
        for k,v in checks.items():
            if not v["Match"]:
                deviations.append(f"{k} ({'Critical' if v['Critical'] else 'Acceptable'})")
                if v["Critical"]:
                    critical_fail = True

        rows.append({
            "SKU": sku["SKU"],
            "Voltage ✓/✗": "✓" if checks["Voltage"]["Match"] else "✗",
            "Insulation ✓/✗": "✓",
            "Standards ✓/✗": "✓" if checks["Standards"]["Match"] else "✗",
            "Conductor ✓/✗": "✓",
            "Spec Match %": match_pct,
            "Deviations": ", ".join(deviations) if deviations else "None",
            "Overall Feasibility": "Reject" if critical_fail else "Feasible",
            "SKU_ID": sku["SKU_ID"]
        })
    return pd.DataFrame(rows).sort_values("Spec Match %", ascending=False)

def pricing_agent(best_sku, rfp):
    unit_price = pricing_master[best_sku["SKU_ID"]]
    quantity = 10
    material_cost = unit_price * quantity
    testing_cost = sum(test_costs[t] for t in rfp["Tests"])
    uplift = 0.1 if best_sku["Spec Match %"] < 90 else 0
    uplift_value = int((material_cost + testing_cost) * uplift)
    final_price = material_cost + testing_cost + uplift_value
    return {
        "Unit Price": unit_price,
        "Quantity": quantity,
        "Material Cost": material_cost,
        "Testing Cost": testing_cost,
        "Risk / MTO Uplift": uplift_value,
        "Final Bid Value": final_price
    }

# =========================================================
# SIDEBAR (MAIN AGENT CONTROL)
# =========================================================
st.sidebar.title("Agents")
agent_view = st.sidebar.radio(
    "Select Agent Dashboard",
    ["Main Agent", "Sales Agent", "Technical Agent", "Pricing Agent", "Final Recommendation"]
)

st.sidebar.markdown("---")
capacity = st.sidebar.slider("Number of bids to pursue", 1, 10, 5)

if st.sidebar.button("▶ Run System"):
    st.session_state.sales_out = sales_agent()
    eligible = st.session_state.sales_out[
        (st.session_state.sales_out["Relevant"]) &
        (st.session_state.sales_out["Priority"] != "Low")
    ]
    st.session_state.selected = eligible.head(capacity)
    st.session_state.capacity_used = capacity
    st.session_state.system_ran = True
    st.session_state.run_timestamp = datetime.now()

# =========================================================
# GLOBAL GUARD
# =========================================================
if not st.session_state.system_ran:
    st.info("Use the Main Agent to select capacity and run the system.")
    st.stop()

sales_out = st.session_state.sales_out
selected = st.session_state.selected

# =========================================================
# MAIN AGENT
# =========================================================
if agent_view == "Main Agent":
    st.markdown("<div class='section amber-box'><h2>🧠 Main Agent — Orchestration & Capacity Control</h2></div>", unsafe_allow_html=True)
    st.write(f"System executed at: {st.session_state.run_timestamp}")
    st.write(f"Bid capacity selected: {st.session_state.capacity_used}")
    st.dataframe(selected.reset_index(drop=True))

# =========================================================
# SALES AGENT
# =========================================================
if agent_view == "Sales Agent":
    st.markdown("<div class='section blue-box'><h2>🧭 Sales Agent — RFP Discovery & Qualification</h2></div>", unsafe_allow_html=True)
    st.dataframe(sales_out.reset_index(drop=True))

# =========================================================
# TECHNICAL AGENT
# =========================================================
if agent_view == "Technical Agent":
    st.markdown("<div class='section blue-box'><h2>🛠 Technical Agent — Specification Matching</h2></div>", unsafe_allow_html=True)
    for _, r in selected.iterrows():
        rfp = rfps[rfps["RFP_ID"] == r["RFP ID"]].iloc[0]
        st.markdown(f"### RFP {rfp['RFP_ID']} — {rfp['Product']}")
        st.dataframe(
            technical_agent(rfp).drop(columns=["SKU_ID"]).reset_index(drop=True),
            use_container_width=True
        )

# =========================================================
# PRICING AGENT
# =========================================================
if agent_view == "Pricing Agent":
    st.markdown("<div class='section green-box'><h2>💰 Pricing Agent — Commercial Evaluation</h2></div>", unsafe_allow_html=True)
    for _, r in selected.iterrows():
        rfp = rfps[rfps["RFP_ID"] == r["RFP ID"]].iloc[0]
        tech = technical_agent(rfp)
        best = tech.iloc[0]
        pricing = pricing_agent(best, rfp)
        st.markdown(f"### RFP {rfp['RFP_ID']} — {rfp['Buyer']} | SKU: {best['SKU']}")
        st.table(pd.DataFrame({
            "Cost Component": pricing.keys(),
            "Amount (₹)": pricing.values()
        }))

# =========================================================
# FINAL RECOMMENDATION
# =========================================================
if agent_view == "Final Recommendation":
    st.markdown("<div class='section green-box'><h2>📊 Final Bid Recommendation</h2></div>", unsafe_allow_html=True)
    final_rows = []
    for _, r in selected.iterrows():
        rfp = rfps[rfps["RFP_ID"] == r["RFP ID"]].iloc[0]
        tech = technical_agent(rfp)
        best = tech.iloc[0]
        pricing = pricing_agent(best, rfp)
        decision = "Bid" if best["Spec Match %"] >= 70 else "No Bid"
        final_rows.append({
            "RFP ID": rfp["RFP_ID"],
            "Buyer": rfp["Buyer"],
            "Product": rfp["Product"],
            "Selected SKU": best["SKU"],
            "Final Bid Value (₹)": pricing["Final Bid Value"],
            "Decision": decision
        })
    st.dataframe(pd.DataFrame(final_rows).reset_index(drop=True), use_container_width=True)
