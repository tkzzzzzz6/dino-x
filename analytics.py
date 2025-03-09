import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from collections import Counter, defaultdict
import altair as alt

class DetectionAnalytics:
    def __init__(self, max_history=100):
        """
        Initialize the detection analytics module
        """
        # Initialize analytics data structures
        if 'object_counts' not in st.session_state:
            st.session_state.object_counts = defaultdict(int)
        
        if 'object_history' not in st.session_state:
            st.session_state.object_history = []
        
        if 'confidence_history' not in st.session_state:
            st.session_state.confidence_history = defaultdict(list)
        
        if 'detection_times' not in st.session_state:
            st.session_state.detection_times = []
        
        self.max_history = max_history
    
    def update_analytics(self, detection_results, detection_time=None):
        """
        Update analytics data with new detection results
        """
        if not detection_results or "objects" not in detection_results:
            return
        
        objects = detection_results["objects"]
        timestamp = time.time()
        
        # Update object counts
        categories = [obj.get("category", "unknown") for obj in objects]
        for category in categories:
            st.session_state.object_counts[category] += 1
        
        # Update object history
        entry = {
            "timestamp": timestamp,
            "total_objects": len(objects),
            "categories": Counter(categories)
        }
        st.session_state.object_history.append(entry)
        
        # Limit history size
        if len(st.session_state.object_history) > self.max_history:
            st.session_state.object_history = st.session_state.object_history[-self.max_history:]
        
        # Update confidence history
        for obj in objects:
            category = obj.get("category", "unknown")
            score = obj.get("score", 0)
            st.session_state.confidence_history[category].append((timestamp, score))
        
        # Limit confidence history size
        for category in st.session_state.confidence_history:
            if len(st.session_state.confidence_history[category]) > self.max_history:
                st.session_state.confidence_history[category] = st.session_state.confidence_history[category][-self.max_history:]
        
        # Update detection times
        if detection_time is not None:
            st.session_state.detection_times.append((timestamp, detection_time))
            
            # Limit detection times history size
            if len(st.session_state.detection_times) > self.max_history:
                st.session_state.detection_times = st.session_state.detection_times[-self.max_history:]
    
    def render_analytics_dashboard(self):
        """
        Render the analytics dashboard
        """
        st.markdown("<h2 class='sub-header'>Analytics Dashboard</h2>", unsafe_allow_html=True)
        
        # 使用单选按钮替代tabs
        analytics_view = st.radio("选择分析视图", ["Object Counts", "Confidence Trends", "Performance"])
        
        if analytics_view == "Object Counts":
            self._render_object_counts()
        
        elif analytics_view == "Confidence Trends":
            self._render_confidence_trends()
        
        elif analytics_view == "Performance":
            self._render_performance_metrics()
    
    def _render_object_counts(self):
        """
        Render object count analytics
        """
        # Object counts
        st.markdown("<h3>Total Object Counts</h3>", unsafe_allow_html=True)
        
        if not st.session_state.object_counts:
            st.info("No detection data available yet.")
            return
        
        # Create a DataFrame for the object counts
        counts_df = pd.DataFrame({
            "Category": list(st.session_state.object_counts.keys()),
            "Count": list(st.session_state.object_counts.values())
        })
        
        # Sort by count in descending order
        counts_df = counts_df.sort_values("Count", ascending=False)
        
        # Create a bar chart
        chart = alt.Chart(counts_df).mark_bar().encode(
            x=alt.X("Category:N", sort="-y"),
            y="Count:Q",
            color=alt.Color("Category:N", legend=None),
            tooltip=["Category", "Count"]
        ).properties(
            width=600,
            height=300
        )
        
        st.altair_chart(chart, use_container_width=True)
        
        # Object history over time
        st.markdown("<h3>Object Detection Timeline</h3>", unsafe_allow_html=True)
        
        if not st.session_state.object_history:
            st.info("No timeline data available yet.")
            return
        
        # Create a DataFrame for the object history
        history_data = []
        for entry in st.session_state.object_history:
            for category, count in entry["categories"].items():
                history_data.append({
                    "timestamp": pd.to_datetime(entry["timestamp"], unit="s"),
                    "category": category,
                    "count": count
                })
        
        history_df = pd.DataFrame(history_data)
        
        if not history_df.empty:
            # Create a line chart
            line_chart = alt.Chart(history_df).mark_line().encode(
                x="timestamp:T",
                y="count:Q",
                color="category:N",
                tooltip=["timestamp", "category", "count"]
            ).properties(
                width=600,
                height=300
            )
            
            st.altair_chart(line_chart, use_container_width=True)
    
    def _render_confidence_trends(self):
        """
        Render confidence trend analytics
        """
        st.markdown("<h3>Confidence Score Trends</h3>", unsafe_allow_html=True)
        
        if not st.session_state.confidence_history:
            st.info("No confidence data available yet.")
            return
        
        # Create a DataFrame for the confidence history
        confidence_data = []
        for category, scores in st.session_state.confidence_history.items():
            for timestamp, score in scores:
                confidence_data.append({
                    "timestamp": pd.to_datetime(timestamp, unit="s"),
                    "category": category,
                    "confidence": score
                })
        
        confidence_df = pd.DataFrame(confidence_data)
        
        if not confidence_df.empty:
            # Create a scatter plot with trend lines
            scatter_chart = alt.Chart(confidence_df).mark_circle(size=60).encode(
                x="timestamp:T",
                y=alt.Y("confidence:Q", scale=alt.Scale(domain=[0, 1])),
                color="category:N",
                tooltip=["timestamp", "category", "confidence"]
            )
            
            line_chart = alt.Chart(confidence_df).mark_line().encode(
                x="timestamp:T",
                y=alt.Y("confidence:Q", scale=alt.Scale(domain=[0, 1])),
                color="category:N"
            )
            
            chart = (scatter_chart + line_chart).properties(
                width=600,
                height=300
            )
            
            st.altair_chart(chart, use_container_width=True)
            
            # Average confidence by category
            st.markdown("<h3>Average Confidence by Category</h3>", unsafe_allow_html=True)
            
            avg_confidence = confidence_df.groupby("category")["confidence"].mean().reset_index()
            avg_confidence = avg_confidence.sort_values("confidence", ascending=False)
            
            bar_chart = alt.Chart(avg_confidence).mark_bar().encode(
                x=alt.X("category:N", sort="-y"),
                y=alt.Y("confidence:Q", scale=alt.Scale(domain=[0, 1])),
                color="category:N",
                tooltip=["category", "confidence"]
            ).properties(
                width=600,
                height=300
            )
            
            st.altair_chart(bar_chart, use_container_width=True)
    
    def _render_performance_metrics(self):
        """
        Render performance metrics
        """
        st.markdown("<h3>Detection Performance</h3>", unsafe_allow_html=True)
        
        if not st.session_state.detection_times:
            st.info("No performance data available yet.")
            return
        
        # Create a DataFrame for the detection times
        times_data = []
        for timestamp, detection_time in st.session_state.detection_times:
            times_data.append({
                "timestamp": pd.to_datetime(timestamp, unit="s"),
                "detection_time": detection_time
            })
        
        times_df = pd.DataFrame(times_data)
        
        if not times_df.empty:
            # Calculate average detection time
            avg_time = times_df["detection_time"].mean()
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Average Detection Time", f"{avg_time:.2f} s")
            
            with col2:
                st.metric("Min Detection Time", f"{times_df['detection_time'].min():.2f} s")
            
            with col3:
                st.metric("Max Detection Time", f"{times_df['detection_time'].max():.2f} s")
            
            # Create a line chart for detection times
            line_chart = alt.Chart(times_df).mark_line().encode(
                x="timestamp:T",
                y="detection_time:Q",
                tooltip=["timestamp", "detection_time"]
            ).properties(
                width=600,
                height=300
            )
            
            st.altair_chart(line_chart, use_container_width=True)
    
    def get_top_objects(self, n=5):
        """
        Get the top N detected objects
        """
        if not st.session_state.object_counts:
            return []
        
        # Sort object counts by count in descending order
        sorted_counts = sorted(st.session_state.object_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return the top N objects
        return sorted_counts[:n] 