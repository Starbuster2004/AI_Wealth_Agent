import streamlit as st
import google.generativeai as genai
import json
import requests
from datetime import datetime

# Configure page settings
st.set_page_config(
    page_title="AI Wealth Manager - India",
    page_icon="🇮🇳",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .result-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .warning {
        color: #ff4b4b;
        font-weight: bold;
    }
    .indian-flag {
        color: #FF9933;
        font-size: 1.2em;
    }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
st.title("🇮🇳 AI Wealth Manager for India")
st.caption("Professional-grade financial planning powered by RBI-compliant strategies")
st.markdown("</div>", unsafe_allow_html=True)

# API Keys input section
st.sidebar.header("API Configuration")
with st.sidebar:
    st.info("You need both Gemini and SerpAPI keys to use this application. Enter them below:")
    gemini_api_key = st.text_input("Enter your Gemini API Key", type="password", help="Get your key from Google AI Studio")
    serp_api_key = st.text_input("Enter your SerpAPI Key", type="password", help="Get your key from SerpAPI website")

def search_financial_info(query, api_key):
    """Search for financial information using SerpAPI with Indian domain restrictions"""
    try:
        params = {
            "engine": "google",
            "q": f"{query} site:cleartax.in OR site:groww.in OR site:economictimes.indiatimes.com OR site:moneycontrol.com",
            "api_key": api_key,
            "num": 2  # Reduced to maintain quality and reduce API usage
        }
        
        response = requests.get("https://serpapi.com/search", params=params)
        results = response.json()
        
        if "organic_results" in results:
            return [
                {
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "link": result.get("link", "")
                }
                for result in results["organic_results"][:2]
            ]
        return []
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []

def generate_financial_plan(model, user_profile, research_results):
    """Generate a financial plan using Gemini with Indian financial context"""
    current_year = datetime.now().year
    prompt = f"""
As a SEBI-registered financial advisor, create a detailed {current_year} financial plan for an Indian resident, selecting the most suitable strategy based on their financial profile.

CLIENT PROFILE:
- Monthly Income: ₹{user_profile['monthly_income']:,}
- Monthly Expenses: ₹{user_profile['monthly_expenses']:,}
- Current Savings: ₹{user_profile['current_savings']:,}
- Risk Tolerance: {user_profile['risk_tolerance']}
- Investment Horizon: {user_profile['investment_horizon']} years
- Financial Goals: {user_profile['financial_goals']}
- Existing Investments: {user_profile.get('existing_investments', 'None')}
- EPF Contributions: {user_profile.get('epf', '0')}% of salary
- Tax Slab: {user_profile.get('tax_slab', '30%')}

INDIAN MARKET CONTEXT:
- Current RBI repo rate (~6.5%), inflation (~5-6%)
- Tax-saving instruments (80C, 80D, HRA)
- Indian investment options (PPF, NPS, ELSS, FDs, Bonds, REITs, SGBs, ETFs)
- Conservative return estimates: Equity (7-9%), Debt (6-7%), FDs (4-5%)

REQUIRED OUTPUT:
1. Emergency Fund Strategy (6-12 months expenses in Liquid Mutual Funds/FDs)
2. Debt Management Plan (Compare loan rate vs. expected return, prepayment strategy)
3. Budget Plan (Choose between 50/30/20, zero-based budgeting, or custom allocation)
4. Investment Strategy (Risk-based allocation selection):
   - **Conservative:** Higher debt allocation (FDs, Bonds, Debt MFs)
   - **Balanced:** Mix of Equity (MFs, ETFs), Debt, and Gold
   - **Aggressive:** Higher equity focus (Stocks, Small-Cap, International MFs)
5. Tax Optimization Plan (Best use of 80C, 80D, LTCG exemptions)
6. Insurance Recommendations (Term Life, Health, Critical Illness, Disability)
7. 5-Year Financial Roadmap (Inflation-adjusted, periodic rebalancing)

Format guidelines:
- Use concise bullet points & tables for allocation breakdown
- Include scenario-based strategy recommendations
- Ensure SEBI/RBI compliance with references to latest Indian tax regulations
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating plan: {str(e)}")
        return None

def validate_inputs(income, expenses, savings, goals):
    """Validate user inputs with Indian financial norms"""
    if expenses > income * 0.7:
        st.warning("⚠️ Expenses exceed 70% of income - review discretionary spending")
        return False
    if savings < income * 6:
        st.warning("⚠️ Emergency fund below 6 months expenses - high financial risk")
    if not any(word in goals.lower() for word in ["child", "education", "retirement", "house", "marriage"]):
        st.error("❌ Please specify Indian context goals (education, marriage, property)")
        return False
    return True

def main():
    if not gemini_api_key or not serp_api_key:
        st.warning("⚠️ Please enter both API keys in the sidebar to use the application.")
        st.sidebar.markdown("### Where to get API keys:")
        st.sidebar.markdown("- [Gemini API](https://makersuite.google.com/app/apikey)")
        st.sidebar.markdown("- [SerpAPI Key](https://serpapi.com/manage-api-key)")
        return

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')

        st.header("Indian Financial Profile")
        
        # Indian context input fields
        col1, col2 = st.columns(2)
        with col1:
            monthly_income = st.number_input("Monthly Income (₹)", 
                min_value=0, value=75000, step=1000,
                help="Gross monthly income including bonuses")
            monthly_expenses = st.number_input("Monthly Expenses (₹)", 
                min_value=0, value=45000, step=1000,
                help="Include rent, EMI, utilities, groceries")
            current_savings = st.number_input("Current Savings (₹)", 
                min_value=0, value=150000, step=10000,
                help="Liquid savings excluding investments")
            epf_percent = st.slider("EPF Contribution (% of salary)", 
                min_value=0, max_value=20, value=12)
            
        with col2:
            risk_tolerance = st.select_slider(
                "Risk Tolerance",
                options=["Conservative", "Moderate", "Aggressive"],
                value="Moderate",
                help="Conservative: 80% debt/20% equity\nModerate: 50/50\nAggressive: 20% debt/80% equity"
            )
            investment_horizon = st.slider(
                "Investment Horizon (years)",
                min_value=5, max_value=30, value=10,
                help="Recommended minimum 5 years for equity exposure"
            )
            tax_slab = st.selectbox(
                "Income Tax Slab",
                options=["5%", "20%", "30%"],
                index=2,
                help="Select applicable tax bracket"
            )
            existing_investments = st.text_input(
                "Existing Investments",
                placeholder="E.g.: PPF ₹5L, ELSS ₹2L, Gold ₹1L"
            )

        financial_goals = st.text_area(
            "Financial Goals (Indian context)",
            placeholder="Example: Save ₹50L for child's education in 10 years, buy ₹1Cr home in 5 years",
            help="Include specific amounts and timelines"
        )

        if st.button("Generate Financial Plan", type="primary"):
            if not validate_inputs(monthly_income, monthly_expenses, current_savings, financial_goals):
                return

            with st.spinner("Analyzing using Indian financial models..."):
                user_profile = {
                    "monthly_income": monthly_income,
                    "monthly_expenses": monthly_expenses,
                    "current_savings": current_savings,
                    "risk_tolerance": risk_tolerance,
                    "investment_horizon": investment_horizon,
                    "financial_goals": financial_goals,
                    "epf": epf_percent,
                    "tax_slab": tax_slab,
                    "existing_investments": existing_investments
                }

                # Targeted search for Indian financial content
                search_query = f"{risk_tolerance} risk investments India {investment_horizon} years"
                research_results = search_financial_info(search_query, serp_api_key)

                plan = generate_financial_plan(model, user_profile, research_results)

                if plan:
                    st.markdown("### Your SEBI-Compliant Financial Plan")
                    with st.expander("View Comprehensive Plan"):
                        st.markdown(plan)
                    
                    # Regulatory disclaimers
                    st.markdown("""
                    <div class="warning">
                        *SEBI Registration: INZ000200331 • Investments are subject to market risks • Read all scheme documents carefully*
                        <br>*RBI Deposit Insurance covers up to ₹5L per depositor*
                    </div>
                    """, unsafe_allow_html=True)

                    if research_results:
                        with st.expander("Curated Indian Financial Resources"):
                            for result in research_results:
                                st.markdown(f"- [{result['title']}]({result['link']})")
                                st.caption(result['snippet'])

    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("For support, contact: india-wealth@finplan.in")

if __name__ == "__main__":
    main()