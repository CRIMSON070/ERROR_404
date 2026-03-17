"""
Team Optimization AI Page for Streamlit Frontend
Deep Learning-powered team evaluation UI
"""

team_optimization_ui_code = '''
elif st.session_state.page == "Team Optimization AI":
    st.title("🔥 Team Optimization AI")
    st.markdown("### Deep Learning-Powered Team Evaluation")
    
    if len(st.session_state.selected_players) < 11:
        st.warning(f"⚠️ You need at least 11 players for optimization. Currently have {len(st.session_state.selected_players)} players.")
        st.info("💡 Go to the Players page and build your team first!")
    else:
        # Team summary cards
        n_players = len(st.session_state.selected_players)
        budget_spent = sum([p.get('sold_price', 0) for p in st.session_state.selected_players])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Team Size", f"{n_players}/25")
        with col2:
            st.metric("Budget Spent", f"₹{budget_spent:.2f} Cr")
        with col3:
            st.metric("Budget Remaining", f"₹{BUDGET_LIMIT - budget_spent:.2f} Cr")
        
        if st.button("🤖 Run AI Optimization Analysis", type="primary"):
            with st.spinner("🧠 AI is analyzing your team..."):
                try:
                    response = requests.get(f"{API_BASE_URL}/team-optimization", timeout=15)
                    
                    if response.status_code == 200:
                        result = response.json()
                        data = result.get('data', {})
                        
                        # Key metrics
                        st.markdown("---")
                        st.subheader("📊 Team Performance Metrics")
                        
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        
                        with metric_col1:
                            efficiency = data.get('efficiency_score', 0)
                            st.metric(
                                "Efficiency Score",
                                f"{efficiency:.2f}",
                                delta="Good" if efficiency > 0.9 else "Needs Improvement"
                            )
                        
                        with metric_col2:
                            total_value = data.get('total_predicted_value', 0)
                            st.metric(
                                "Predicted Team Value",
                                f"₹{total_value:.2f} Cr",
                                delta=f"₹{total_value - budget_spent:+.2f} Cr"
                            )
                        
                        with metric_col3:
                            avg_perf = data.get('average_performance', 0)
                            st.metric(
                                "Avg Performance",
                                f"{avg_perf:.1f}/100",
                                delta="Excellent" if avg_perf > 70 else "Average"
                            )
                        
                        # Visualizations
                        st.markdown("---")
                        st.subheader("💰 Value vs Cost Analysis")
                        
                        df_comparison = pd.DataFrame({
                            'Metric': ['Actual Cost', 'Predicted Value'],
                            'Value (₹ Cr)': [budget_spent, total_value]
                        })
                        
                        fig = px.bar(
                            df_comparison,
                            x='Metric',
                            y='Value (₹ Cr)',
                            color='Metric',
                            color_discrete_map={'Actual Cost': '#ff6b6b', 'Predicted Value': '#4CAF50'},
                            title='Team Value vs Actual Cost'
                        )
                        fig.update_layout(template="plotly_dark")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Overpriced and undervalued players
                        st.markdown("---")
                        overpriced = data.get('overpriced_players', [])
                        undervalued = data.get('undervalued_players', [])
                        
                        col_over, col_under = st.columns(2)
                        
                        with col_over:
                            st.markdown(f"### 🔴 Overpriced Players ({len(overpriced)})")
                            if overpriced:
                                for player in overpriced[:5]:
                                    st.markdown(f"""
                                    <div style="background-color: rgba(255, 107, 107, 0.1); padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #ff6b6b;">
                                        <strong>{player['player_name']}</strong><br>
                                        <small>Role: {player['role']} | Price: ₹{player['actual_price']:.2f}Cr | Value: ₹{player['predicted_value']:.2f}Cr</small><br>
                                        <small>Risk: {player['risk_score']:.2f} | Status: Overpriced by ₹{player['actual_price'] - player['predicted_value']:.2f}Cr</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.success("✅ No overpriced players!")
                        
                        with col_under:
                            st.markdown(f"### 🟢 Undervalued Players ({len(undervalued)})")
                            if undervalued:
                                for player in undervalued[:5]:
                                    st.markdown(f"""
                                    <div style="background-color: rgba(76, 175, 80, 0.1); padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #4CAF50;">
                                        <strong>{player['player_name']}</strong><br>
                                        <small>Role: {player['role']} | Price: ₹{player['actual_price']:.2f}Cr | Value: ₹{player['predicted_value']:.2f}Cr</small><br>
                                        <small>Surplus: +₹{player['predicted_value'] - player['actual_price']:.2f}Cr | Great value pick!</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("No significantly undervalued players found")
                        
                        # Replacement suggestions
                        st.markdown("---")
                        st.subheader("🔁 Replacement Opportunities")
                        
                        replacement_opps = data.get('replacement_opportunities', [])
                        
                        if replacement_opps:
                            for opp in replacement_opps:
                                replace_player = opp.get('replace_player', '')
                                suggestions = opp.get('suggestions', [])
                                
                                st.markdown(f"""
                                <div style="background-color: #1a1f2e; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                                    <h4 style="margin-top: 0;">Replace: {replace_player}</h4>
                                    <p style="color: #ff6b6b;"><strong>Reason:</strong> {opp.get('reason', 'Overpriced')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                for i, sug in enumerate(suggestions, 1):
                                    st.markdown(f"""
                                    <div style="background-color: rgba(76, 175, 80, 0.1); padding: 12px; border-radius: 5px; margin-bottom: 10px; margin-left: 20px; border-left: 4px solid #4CAF50;">
                                        <strong>Suggestion {i}: {sug['suggested_player']}</strong> ({sug['role']})<br>
                                        <small>Predicted Value: ₹{sug['predicted_value']:.2f}Cr | Price: ₹{sug['predicted_price']:.2f}Cr</small><br>
                                        <small>Performance: {sug['performance_score']:.1f}/100 | Risk: {sug['risk_score']:.2f}</small><br>
                                        <em style="color: #4CAF50;">💡 {sug['reason']}</em>
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.success("✅ Your team is well optimized! No critical replacements needed.")
                        
                        # Recommendations
                        st.markdown("---")
                        st.subheader("💡 AI Recommendations")
                        recommendations = data.get('recommendations', [])
                        
                        for rec in recommendations:
                            icon = "✅" if "Good" in rec or "Great" in rec else "⚠️" if "Critical" in rec else "💡"
                            st.write(f"{icon} {rec}")
                    
                    else:
                        st.error(f"Failed to get analysis from API. Status: {response.status_code}")
                
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info("💡 Make sure the backend server is running and models are trained.")
'''
