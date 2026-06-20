import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io


pd.read_excel("all_together.xlsx")


# Page configuration
st.set_page_config(
    page_title="BUCLEY INC ",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

class FashionInventoryAnalyzer:
    def __init__(self, data):
        self.df = data
        self.clean_data()
    
    def clean_data(self):
        """Clean and preprocess the data"""
        # Create a copy to avoid modifying original
        df_clean = self.df.copy()
        
        # Remove completely empty rows
        df_clean = df_clean.dropna(how='all')
        
        # Clean numeric columns
        numeric_columns = ['Quantity', 'Price', 'Total', 'WholeSale']
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Clean text columns
        text_columns = ['Serial_No', 'Dukanka', 'Type']
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
        
        self.df_clean = df_clean
    
    def get_summary_metrics(self):
        """Calculate key performance metrics"""
        metrics = {}
        
        if 'Total' in self.df_clean.columns:
            metrics['total_revenue'] = self.df_clean['Total'].sum()
            metrics['avg_price'] = self.df_clean['Price'].mean()
            metrics['total_quantity'] = self.df_clean['Quantity'].sum()
        
        if 'Dukanka' in self.df_clean.columns:
            metrics['unique_suppliers'] = self.df_clean['Dukanka'].nunique()
        
        if 'Type' in self.df_clean.columns:
            metrics['product_categories'] = self.df_clean['Type'].nunique()
        
        return metrics
    
    def get_supplier_analysis(self):
        """Analyze performance by supplier"""
        supplier_stats = self.df_clean.groupby('Dukanka').agg({
            'Total': 'sum',
            'Quantity': 'sum',
            'Price': 'mean',
            'Serial_No': 'count'
        }).rename(columns={'Serial_No': 'Product_Count'})
        
        supplier_stats['Avg_Price'] = supplier_stats['Total'] / supplier_stats['Quantity']
        return supplier_stats.sort_values('Total', ascending=False)
    
    def get_category_analysis(self):
        """Analyze performance by product category"""
        category_stats = self.df_clean.groupby('Type').agg({
            'Total': 'sum',
            'Quantity': 'sum',
            'Price': 'mean',
            'Serial_No': 'count'
        }).rename(columns={'Serial_No': 'Product_Count'})
        
        return category_stats.sort_values('Total', ascending=False)

def main():
    # Title and description
    st.markdown('<h1 class="main-header">👗 BUCLEY SHOP DASHBOARD</h1>', unsafe_allow_html=True)
    
    # Load and process data
    @st.cache_data
    def load_data():
        # Convert the provided data to DataFrame
        data = pd.read_excel('Merged_File.xlsx')  # In practice, you'd upload the file
        return data
    
    # For demo purposes, we'll create sample data based on the provided structure
    def create_sample_data():
        # This would be replaced with actual file upload
        sample_data = pd.DataFrame({
            'Serial_No': ['8440', '7715', '2596#', '2508', '50', '2199-3', '8399', '5700#'],
            'Dukanka': ['Ramadan-B7', 'Ramadan-B7', 'Ramadan-B7', 'Ramadan-B7', 'L109', 'L108', 'L109', 'L109'],
            'Quantity': [12, 12, 12, 12, 12, 12, 12, 12],
            'Price': [500, 550, 500, 600, 300, 470, 450, 600],
            'Type': ['Short dress', 'Short dress', 'Short dress', 'Short dress', 'skirt', 'Short dress', 'Short dress', 'Short dress'],
            'Total': [6000, 6600, 6000, 7200, 3600, 5640, 5400, 7200],
            'WholeSale': [750, 750, 750, 800, 350, 650, 650, 700]
        })
        return sample_data
    
    # File upload
    uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx'])
    
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
    else:
        st.info("Using sample data for demonstration. Please upload an Excel file for your actual data.")
        data = create_sample_data()
    
    # Initialize analyzer
    analyzer = FashionInventoryAnalyzer(data)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Supplier filter
    suppliers = ['All'] + sorted(analyzer.df_clean['Dukanka'].unique().tolist())
    selected_supplier = st.sidebar.selectbox("Select Supplier", suppliers)
    
    # Product type filter
    product_types = ['All'] + sorted(analyzer.df_clean['Type'].unique().tolist())
    selected_type = st.sidebar.selectbox("Select Product Type", product_types)
    
    # Price range filter
    if 'Price' in analyzer.df_clean.columns:
        min_price = float(analyzer.df_clean['Price'].min())
        max_price = float(analyzer.df_clean['Price'].max())
        price_range = st.sidebar.slider(
            "Price Range",
            min_price, max_price, (min_price, max_price)
        )
    
    # Apply filters
    filtered_data = analyzer.df_clean.copy()
    if selected_supplier != 'All':
        filtered_data = filtered_data[filtered_data['Dukanka'] == selected_supplier]
    if selected_type != 'All':
        filtered_data = filtered_data[filtered_data['Type'] == selected_type]
    if 'Price' in analyzer.df_clean.columns:
        filtered_data = filtered_data[
            (filtered_data['Price'] >= price_range[0]) & 
            (filtered_data['Price'] <= price_range[1])
        ]
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = analyzer.get_summary_metrics()
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Revenue", f"${metrics.get('total_revenue', 0):,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Average Price", f"${metrics.get('avg_price', 0):.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Quantity", f"{metrics.get('total_quantity', 0):,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Product Categories", f"{metrics.get('product_categories', 0)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts and Analysis
    st.markdown("---")
    
    # Two main columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Revenue by Supplier")
        supplier_analysis = analyzer.get_supplier_analysis()
        
        if not supplier_analysis.empty:
            fig = px.bar(
                supplier_analysis.head(10),
                x=supplier_analysis.head(10).index,
                y='Total',
                color='Total',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                xaxis_title="Supplier",
                yaxis_title="Total Revenue",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🎯 Price Distribution")
        if 'Price' in filtered_data.columns:
            fig = px.histogram(
                filtered_data, 
                x='Price',
                nbins=20,
                color_discrete_sequence=['#1f77b4']
            )
            fig.update_layout(
                xaxis_title="Price",
                yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Revenue by Category")
        category_analysis = analyzer.get_category_analysis()
        
        if not category_analysis.empty:
            fig = px.pie(
                category_analysis,
                values='Total',
                names=category_analysis.index,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📦 Quantity vs Price Analysis")
        if all(col in filtered_data.columns for col in ['Quantity', 'Price', 'Type']):
            fig = px.scatter(
                filtered_data,
                x='Price',
                y='Quantity',
                color='Type',
                size='Total',
                hover_data=['Serial_No', 'Dukanka']
            )
            fig.update_layout(
                xaxis_title="Price",
                yaxis_title="Quantity"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Analysis Section
    st.markdown("---")
    st.subheader("🔍 Detailed Analysis")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Data Overview", "💰 Supplier Performance", "👗 Category Insights", "📊 Advanced Analytics"])
    
    with tab1:
        st.dataframe(filtered_data, use_container_width=True)
        
        # Data summary
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Data Summary:**")
            st.write(f"Total Records: {len(filtered_data)}")
            st.write(f"Unique Suppliers: {filtered_data['Dukanka'].nunique()}")
            st.write(f"Product Types: {filtered_data['Type'].nunique()}")
        
        with col2:
            st.write("**Price Statistics:**")
            if 'Price' in filtered_data.columns:
                st.write(f"Min Price: ${filtered_data['Price'].min():.0f}")
                st.write(f"Max Price: ${filtered_data['Price'].max():.0f}")
                st.write(f"Median Price: ${filtered_data['Price'].median():.0f}")
    
    with tab2:
        supplier_performance = analyzer.get_supplier_analysis()
        st.dataframe(supplier_performance, use_container_width=True)
        
        # Supplier comparison
        st.subheader("Supplier Comparison")
        col1, col2 = st.columns(2)
        
        with col1:
            if not supplier_performance.empty:
                fig = px.bar(
                    supplier_performance.head(8),
                    y=supplier_performance.head(8).index,
                    x='Total',
                    orientation='h',
                    color='Total',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not supplier_performance.empty:
                fig = px.scatter(
                    supplier_performance,
                    x='Product_Count',
                    y='Avg_Price',
                    size='Total',
                    color='Total',
                    hover_data=[supplier_performance.index],
                    color_continuous_scale='Plasma'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        category_insights = analyzer.get_category_analysis()
        st.dataframe(category_insights, use_container_width=True)
        
        # Category trends
        st.subheader("Category Performance Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not category_insights.empty:
                # FIXED: Reset index to avoid the "Type" ambiguity issue
                category_insights_reset = category_insights.reset_index()
                fig = px.treemap(
                    category_insights_reset,
                    path=['Type'],  # Use the column name instead of index
                    values='Total',
                    color='Total',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not category_insights.empty:
                fig = px.box(
                    filtered_data,
                    x='Type',
                    y='Price',
                    color='Type'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Advanced Business Intelligence")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Inventory turnover analysis
            st.write("**Inventory Efficiency**")
            if all(col in filtered_data.columns for col in ['Quantity', 'Total']):
                efficiency_data = filtered_data.groupby('Dukanka').agg({
                    'Quantity': 'sum',
                    'Total': 'sum'
                })
                efficiency_data['Revenue_per_Unit'] = efficiency_data['Total'] / efficiency_data['Quantity']
                
                fig = px.scatter(
                    efficiency_data,
                    x='Quantity',
                    y='Revenue_per_Unit',
                    size='Total',
                    color=efficiency_data.index,
                    title="Inventory Efficiency by Supplier"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Price optimization analysis - FIXED VERSION
            st.write("**Price Optimization Insights**")
            if 'Price' in filtered_data.columns:
                # Create custom price segments with string labels instead of Interval objects
                price_bins = [0, 200, 400, 600, 800, 1000, float('inf')]
                price_labels = ['0-200', '201-400', '401-600', '601-800', '801-1000', '1000+']
                
                filtered_data['Price_Segment'] = pd.cut(
                    filtered_data['Price'], 
                    bins=price_bins, 
                    labels=price_labels,
                    right=False
                )
                
                segment_analysis = filtered_data.groupby('Price_Segment').agg({
                    'Quantity': 'sum',
                    'Total': 'sum',
                    'Serial_No': 'count'
                }).rename(columns={'Serial_No': 'Product_Count'}).reset_index()
                
                fig = px.line(
                    segment_analysis,
                    x='Price_Segment',
                    y=['Quantity', 'Product_Count'],
                    title="Demand vs Price Segments",
                    markers=True
                )
                fig.update_layout(
                    xaxis_title="Price Segments",
                    yaxis_title="Count"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Recommendation engine
        st.subheader("💡 Business Recommendations")
        
        if not supplier_performance.empty and not category_insights.empty:
            top_supplier = supplier_performance.index[0]
            top_category = category_insights.index[0]
            
            # Calculate average margin if wholesale data is available
            if 'WholeSale' in filtered_data.columns:
                avg_margin = (filtered_data['Price'] - filtered_data['WholeSale']).mean()
            else:
                avg_margin = (filtered_data['Price'] * 0.4).mean()  # Estimate 40% margin
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info(f"**Focus Supplier**: {top_supplier}")
                st.write(f"Highest revenue generator with ${supplier_performance.loc[top_supplier, 'Total']:,.0f}")
            
            with col2:
                st.success(f"**Top Category**: {top_category}")
                st.write(f"Leading category with ${category_insights.loc[top_category, 'Total']:,.0f} revenue")
            
            with col3:
                if avg_margin > 0:
                    st.warning(f"**Avg Margin**: ${avg_margin:.0f}")
                    st.write("Monitor wholesale vs retail pricing")
        
    # Export functionality
    st.markdown("---")
    st.subheader("📤 Export Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export Filtered Data to CSV"):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="filtered_inventory_data.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Export Supplier Analysis"):
            csv = analyzer.get_supplier_analysis().to_csv()
            st.download_button(
                label="Download Supplier Analysis",
                data=csv,
                file_name="supplier_analysis.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("Export Category Analysis"):
            csv = analyzer.get_category_analysis().to_csv()
            st.download_button(
                label="Download Category Analysis",
                data=csv,
                file_name="category_analysis.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()