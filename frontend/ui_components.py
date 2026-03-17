"""
Enhanced Streamlit UI with Modern Design & IPL Branding
Professional-grade dashboard with animations and DL insights
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import base64

# ==================== PAGE CONFIGURATION ====================

def set_page_config():
    """Configure page with modern settings"""
    st.set_page_config(
        page_title="IPL Auction Strategy Platform",
        page_icon="🏏",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# ==================== CUSTOM CSS STYLING ====================

def load_custom_css():
    """Load advanced CSS styling"""
    
    # Check if assets folder exists and logo exists
    import os
    logo_path = "assets/ipl_logo.png"
    has_logo = os.path.exists(logo_path)
    
    if has_logo:
        # Encode logo for data URI (better performance)
        try:
            with open(logo_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                logo_url = f"data:image/png;base64,{encoded_string}"
        except:
            logo_url = ""
    else:
        logo_url = ""
    
    # Build background CSS based on logo availability
    if logo_url:
        background_css = f"""
        .stApp {{
            background-image: url("{logo_url}");
            background-size: 40%;
            background-repeat: no-repeat;
            background-position: center;
            background-attachment: fixed;
            opacity: 0.98;
        }}
        """
    else:
        # Fallback gradient if no logo
        background_css = """
        .stApp {
            background: linear-gradient(135deg, rgba(10,25,47,0.95) 0%, rgba(18,38,64,0.95) 100%);
        }
        """
    
    st.markdown(f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {{
        font-family: 'Inter', sans-serif !important;
    }}
    
    {background_css}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0A192F 0%, #122640 100%);
        border-right: 2px solid #1e3a5f;
    }}
    
    [data-testid="stSidebar"] .css-1d399n1 {{
        color: #E6F1FF !important;
    }}
    
    /* Navigation Menu Items */
    .stSidebar .stButton > button {{
        width: 100%;
        padding: 12px 16px;
        margin: 4px 0;
        background: transparent;
        border: 2px solid transparent;
        border-radius: 8px;
        color: #E6F1FF;
        font-weight: 500;
        transition: all 0.3s ease;
        text-align: left;
        cursor: pointer;
    }}
    
    .stSidebar .stButton > button:hover {{
        background: rgba(100, 200, 255, 0.1);
        border-color: #64C8FF;
        box-shadow: 0 0 15px rgba(100, 200, 255, 0.3);
    }}
    
    .stSidebar .stButton > button.active {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: #764ba2;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4);
    }}
    
    /* Main Container */
    .main-container {{
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }}
    
    /* Card Styling */
    .metric-card {{
        background: linear-gradient(135deg, rgba(26, 31, 46, 0.9) 0%, rgba(38, 46, 66, 0.9) 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(100, 200, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        border-color: rgba(100, 200, 255, 0.3);
        box-shadow: 0 8px 30px rgba(100, 200, 255, 0.2);
    }}
    
    /* Metric Value */
    .metric-value {{
        font-size: 2.5em;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 5px;
    }}
    
    .metric-label {{
        font-size: 0.9em;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }}
    
    /* Player Card */
    .player-card {{
        background: linear-gradient(135deg, rgba(26, 31, 46, 0.95) 0%, rgba(38, 46, 66, 0.95) 100%);
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #667eea;
        margin-bottom: 12px;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    .player-card:hover {{
        transform: translateX(5px);
        border-left-color: #764ba2;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }}
    
    .player-name {{
        font-size: 1.1em;
        font-weight: 600;
        color: #E6F1FF;
        margin-bottom: 4px;
    }}
    
    .player-info {{
        font-size: 0.85em;
        color: #94A3B8;
    }}
    
    .player-stats {{
        display: flex;
        gap: 12px;
        margin-top: 8px;
    }}
    
    .stat-badge {{
        background: rgba(102, 126, 234, 0.15);
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8em;
        color: #667eea;
        font-weight: 600;
    }}
    
    /* Status Indicators */
    .status-overpriced {{
        background: rgba(255, 107, 107, 0.15);
        border-left: 4px solid #ff6b6b;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }}
    
    .status-undervalued {{
        background: rgba(76, 175, 80, 0.15);
        border-left: 4px solid #4CAF50;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }}
    
    .status-fair {{
        background: rgba(255, 193, 7, 0.15);
        border-left: 4px solid #FFC107;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }}
    
    /* AI Badge */
    .ai-badge {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.75em;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 8px;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }}
    
    /* Progress Bar */
    .progress-container {{
        width: 100%;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        overflow: hidden;
        height: 12px;
        margin: 10px 0;
    }}
    
    .progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: width 1s ease-in-out;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
    }}
    
    /* Section Headers */
    .section-header {{
        font-size: 1.8em;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
    }}
    
    /* Alert Boxes */
    .alert-box {{
        padding: 15px 20px;
        border-radius: 8px;
        margin: 15px 0;
        border-left: 4px solid;
        animation: slideIn 0.5s ease;
    }}
    
    .alert-info {{
        background: rgba(100, 200, 255, 0.1);
        border-color: #64C8FF;
        color: #E6F1FF;
    }}
    
    .alert-warning {{
        background: rgba(255, 193, 7, 0.1);
        border-color: #FFC107;
        color: #FFF3CD;
    }}
    
    .alert-success {{
        background: rgba(76, 175, 80, 0.1);
        border-color: #4CAF50;
        color: #D4EDDA;
    }}
    
    /* Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(-20px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.6; }}
    }}
    
    .fade-in {{
        animation: fadeIn 0.6s ease;
    }}
    
    .pulse {{
        animation: pulse 2s infinite;
    }}
    
    /* Button Styling */
    .stButton > button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }}
    
    /* Table Styling */
    .dataframe {{
        background: rgba(26, 31, 46, 0.9);
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid rgba(100, 200, 255, 0.1);
    }}
    
    .dataframe th {{
        background: rgba(102, 126, 234, 0.2);
        color: #667eea;
        font-weight: 600;
        padding: 12px;
    }}
    
    .dataframe td {{
        color: #E6F1FF;
        padding: 10px;
    }}
    
    /* Chart Containers */
    .chart-container {{
        background: rgba(26, 31, 46, 0.9);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(100, 200, 255, 0.1);
        margin-bottom: 20px;
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(255, 255, 255, 0.05);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: #764ba2;
    }}
    
    </style>
    """, unsafe_allow_html=True)

# ==================== SIDEBAR NAVIGATION ====================

def render_sidebar(selected_page):
    """Render sidebar with navigation and branding"""
    
    with st.sidebar:
        # Logo and Title
        col1, col2 = st.columns([1, 3])
        with col1:
            # Try to load logo if available
            import os
            logo_path = "assets/ipl_logo.png"
            if os.path.exists(logo_path):
                try:
                    logo = Image.open(logo_path)
                    st.image(logo, width=60)
                except:
                    st.markdown("🏏")
            else:
                st.markdown("🏏")
        
        with col2:
            st.markdown("""
            <div style='margin-top: 10px;'>
                <h3 style='color: #E6F1FF; margin: 0; font-weight: 700;'>IPL AUCTION</h3>
                <p style='color: #667eea; margin: 0; font-size: 0.8em;'>STRATEGY PLATFORM</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation Menu
        pages = [
            ("Home", "🏠"),
            ("Players", "👥"),
            ("Team Builder", "🛠️"),
            ("Analytics", "📊"),
            ("AI Suggestions", "🤖"),
            ("Best XI", "⭐"),
            ("Team Optimization AI", "🔥"),
            ("Auction Strategy", "💼")
        ]
        
        for page_name, icon in pages:
            is_active = (page_name == selected_page)
            
            # Create button with active state
            if st.button(
                f"{icon} {page_name}",
                key=f"nav_{page_name}",
                use_container_width=True
            ):
                st.session_state.page = page_name
                st.rerun()
        
        st.markdown("---")
        
        # Budget Summary in Sidebar
        if 'selected_players' in st.session_state:
            budget_spent = sum([p.get('sold_price', 0) for p in st.session_state.selected_players])
            budget_remaining = 120 - budget_spent
            players_count = len(st.session_state.selected_players)
            
            st.markdown("### 💰 Budget Overview")
            
            # Budget Progress
            budget_pct = min((budget_spent / 120) * 100, 100)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Budget Remaining</div>
                <div class="metric-value" style="font-size: 2em;">₹{budget_remaining:.1f} Cr</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {budget_pct}%;"></div>
                </div>
                <div style="font-size: 0.8em; color: #94A3B8; text-align: center;">
                    ₹{budget_spent:.1f} Cr used of ₹120 Cr
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='text-align: center; margin-top: 15px; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;'>
                <strong style='color: #667eea;'>👥 {players_count}/25</strong>
                <span style='color: #94A3B8; font-size: 0.9em;'> Players Selected</span>
            </div>
            """, unsafe_allow_html=True)

# ==================== METRIC CARDS ====================

def metric_card(title, value, delta=None, icon="📊"):
    """Create a beautiful metric card"""
    
    delta_html = ""
    if delta is not None:
        # Handle both numeric and string deltas
        if isinstance(delta, (int, float)):
            delta_color = "green" if delta > 0 else "red"
            delta_sign = "+" if delta > 0 else ""
            delta_html = f"<span style='color: #{'4CAF50' if delta > 0 else 'ff6b6b'}; font-size: 0.9em;'>{delta_sign}{delta}</span>"
        elif isinstance(delta, str):
            # For string deltas like percentages, just display them
            delta_html = f"<span style='color: #667eea; font-size: 0.9em;'>{delta}</span>"
    
    return f"""
    <div class="metric-card fade-in">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 1.5em;">{icon}</span>
            {delta_html}
        </div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
    </div>
    """

# ==================== PLAYER CARD COMPONENT ====================

def player_card(player_data, show_dl_insights=True, can_add=True, on_add=None):
    """Create an interactive player card with DL insights"""
    
    name = player_data.get('player_name', 'Unknown')
    role = player_data.get('role', 'Unknown')
    team = player_data.get('team', '-')
    price = player_data.get('sold_price', 0)
    base_price = player_data.get('base_price', 0)
    
    # DL Insights (if available)
    ai_score = player_data.get('ai_score', None)
    predicted_value = player_data.get('predicted_value', None)
    risk_score = player_data.get('risk_score', None)
    performance_score = player_data.get('performance_score', None)
    
    # Determine status
    if predicted_value:
        if predicted_value > price * 1.2:
            status = "undervalued"
            status_text = "🟢 Undervalued"
        elif predicted_value < price * 0.8:
            status = "overpriced"
            status_text = "🔴 Overpriced"
        else:
            status = "fair"
            status_text = "🟡 Fair Value"
    else:
        status = "fair"
        status_text = ""
    
    card_html = f"""
    <div class="player-card" onclick="this.style.transform='scale(1.02)'">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div style="flex: 1;">
                <div class="player-name">{name}</div>
                <div class="player-info">{role} • {team}</div>
                <div class="player-stats">
                    <span class="stat-badge">₹{price:.2f} Cr</span>
                    {f'<span class="stat-badge">Base: ₹{base_price:.2f} Cr</span>' if base_price else ''}
                </div>
            </div>
        </div>
    """
    
    # Add DL Insights if available
    if show_dl_insights and (ai_score or predicted_value or performance_score):
        card_html += """
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(102, 126, 234, 0.2);">
            <div class="ai-badge">🤖 AI INSIGHTS</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px;">
        """
        
        if ai_score:
            card_html += f"""
            <div style="background: rgba(102, 126, 234, 0.1); padding: 6px; border-radius: 6px;">
                <div style="font-size: 0.75em; color: #94A3B8;">AI Score</div>
                <div style="font-size: 1.1em; color: #667eea; font-weight: 700;">{ai_score:.1f}</div>
            </div>
            """
        
        if predicted_value:
            card_html += f"""
            <div style="background: rgba(118, 75, 162, 0.1); padding: 6px; border-radius: 6px;">
                <div style="font-size: 0.75em; color: #94A3B8;">Pred. Value</div>
                <div style="font-size: 1.1em; color: #764ba2; font-weight: 700;">₹{predicted_value:.2f} Cr</div>
            </div>
            """
        
        if performance_score:
            card_html += f"""
            <div style="background: rgba(76, 175, 80, 0.1); padding: 6px; border-radius: 6px;">
                <div style="font-size: 0.75em; color: #94A3B8;">Performance</div>
                <div style="font-size: 1.1em; color: #4CAF50; font-weight: 700;">{performance_score:.1f}/100</div>
            </div>
            """
        
        if risk_score is not None:
            card_html += f"""
            <div style="background: rgba(255, 193, 7, 0.1); padding: 6px; border-radius: 6px;">
                <div style="font-size: 0.75em; color: #94A3B8;">Risk</div>
                <div style="font-size: 1.1em; color: {'#4CAF50' if risk_score < 0.3 else '#FFC107' if risk_score < 0.6 else '#ff6b6b'}; font-weight: 700;">{risk_score:.2f}</div>
            </div>
            """
        
        card_html += """
            </div>
        """
        
        if status_text:
            card_html += f"""
            <div style="margin-top: 8px; font-size: 0.85em; color: #94A3B8;">
                {status_text}
            </div>
            """
        
        card_html += """
        </div>
        """
    
    # Add button if actionable
    if can_add:
        card_html += f"""
        <div style="margin-top: 12px;">
            <button style="width: 100%; padding: 8px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 6px; color: white; font-weight: 600; cursor: pointer;">
                ➕ Add to Team
            </button>
        </div>
        """
    
    card_html += "</div>"
    
    return card_html

# ==================== CHART COMPONENTS ====================

def create_budget_chart(budget_spent, budget_total=120):
    """Create animated budget gauge chart"""
    
    budget_pct = (budget_spent / budget_total) * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=budget_spent,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': "<b>BUDGET UTILIZATION</b>",
            'font': {'size': 16, 'color': '#E6F1FF'}
        },
        delta={'reference': budget_total * 0.7},
        gauge={
            'axis': {
                'range': [None, budget_total],
                'tickwidth': 2,
                'tickcolor': "#4A5568"
            },
            'bar': {
                'color': "#667eea",
                'thickness': 0.5
            },
            'bgcolor': "rgba(26, 31, 46, 0.5)",
            'borderwidth': 2,
            'bordercolor': "#667eea",
            'steps': [
                {'range': [0, budget_total * 0.6], 'color': 'rgba(76, 175, 80, 0.2)'},
                {'range': [budget_total * 0.6, budget_total * 0.85], 'color': 'rgba(255, 193, 7, 0.2)'},
                {'range': [budget_total * 0.85, budget_total], 'color': 'rgba(255, 107, 107, 0.2)'}
            ],
        }
    ))
    
    fig.update_layout(
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=20, l=20, r=20)
    )
    
    return fig

def create_team_composition_chart(players):
    """Create pie chart for team composition"""
    
    if not players:
        return None
    
    # Count roles
    role_counts = {}
    for player in players:
        role = player.get('role', 'Unknown')
        # Simplify role names
        if 'Wicket-keeper' in role:
            role = 'WK'
        elif 'Batsman' in role:
            role = 'BAT'
        elif 'All-rounder' in role:
            role = 'AR'
        elif 'Bowler' in role:
            role = 'BOWL'
        
        role_counts[role] = role_counts.get(role, 0) + 1
    
    labels = list(role_counts.keys())
    values = list(role_counts.values())
    
    fig = px.pie(
        values=values,
        names=labels,
        title='<b>TEAM COMPOSITION</b>',
        color_discrete_sequence=['#667eea', '#764ba2', '#4CAF50', '#FFC107'],
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )
    
    fig.update_layout(
        height=300,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font_size=16,
        margin=dict(t=40, b=20, l=20, r=20)
    )
    
    return fig

def create_value_distribution_chart(players):
    """Create histogram of player values"""
    
    if not players:
        return None
    
    prices = [p.get('sold_price', 0) for p in players]
    
    fig = px.histogram(
        x=prices,
        nbins=10,
        title='<b>PLAYER VALUE DISTRIBUTION</b>',
        labels={'x': 'Price (₹ Cr)', 'y': 'Count'},
        color_discrete_sequence=['#667eea']
    )
    
    fig.update_layout(
        height=300,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font_size=16,
        xaxis_title_font=dict(color='#E6F1FF'),
        yaxis_title_font=dict(color='#E6F1FF'),
        xaxis_tickfont=dict(color='#94A3B8'),
        yaxis_tickfont=dict(color='#94A3B8'),
        margin=dict(t=40, b=40, l=40, r=20)
    )
    
    return fig

# ==================== LOADING ANIMATIONS ====================

def ai_loading_animation(message="🤖 AI is analyzing..."):
    """Display AI loading animation"""
    
    st.markdown(f"""
    <div style="text-align: center; padding: 40px;">
        <div class="pulse" style="font-size: 3em; margin-bottom: 20px;">🧠</div>
        <div style="color: #667eea; font-size: 1.2em; font-weight: 600;">{message}</div>
        <div style="margin-top: 20px;">
            <div class="progress-container" style="max-width: 300px; margin: 20px auto;">
                <div class="progress-bar" style="width: 0%; animation: progressAnimation 2s infinite;"></div>
            </div>
        </div>
    </div>
    
    <style>
    @keyframes progressAnimation {{
        0% {{ width: 0%; }}
        50% {{ width: 70%; }}
        100% {{ width: 0%; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ==================== ALERT COMPONENTS ====================

def alert_box(message, type="info"):
    """Create styled alert boxes"""
    
    icons = {
        "info": "💡",
        "warning": "⚠️",
        "success": "✅",
        "error": "❌"
    }
    
    icon = icons.get(type, "ℹ️")
    
    st.markdown(f"""
    <div class="alert-box alert-{type}">
        <strong>{icon}</strong> {message}
    </div>
    """, unsafe_allow_html=True)

# ==================== EXPORT FUNCTIONS ====================

__all__ = [
    'set_page_config',
    'load_custom_css',
    'render_sidebar',
    'metric_card',
    'player_card',
    'create_budget_chart',
    'create_team_composition_chart',
    'create_value_distribution_chart',
    'ai_loading_animation',
    'alert_box'
]
