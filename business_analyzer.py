import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

class BusinessAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def top_selling_products(self, n=5):
        if 'Product Name' in self.df.columns and 'Revenue' in self.df.columns:
            top = self.df.groupby('Product Name')['Revenue'].sum().sort_values(ascending=False).head(n)
            return top
        return None

    def top_selling_categories(self, n=5):
        if 'Product Category' in self.df.columns and 'Revenue' in self.df.columns:
            top = self.df.groupby('Product Category')['Revenue'].sum().sort_values(ascending=False).head(n)
            return top
        return None

    def sales_trends(self):
        if 'Date' in self.df.columns and 'Revenue' in self.df.columns:
            self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
            trend = self.df.groupby(self.df['Date'].dt.to_period('M'))['Revenue'].sum()
            return trend
        return None

    def regional_performance(self):
        if 'Region' in self.df.columns and 'Revenue' in self.df.columns:
            region = self.df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)
            return region
        return None

    def customer_segment_analysis(self):
        if 'Customer Segment' in self.df.columns and 'Revenue' in self.df.columns:
            segment = self.df.groupby('Customer Segment')['Revenue'].sum()
            return segment
        return None

    def summary_statistics(self):
        if 'Revenue' in self.df.columns:
            stats = self.df['Revenue'].describe()
            return stats
        return None

    def anomalies(self):
        if 'Revenue' in self.df.columns:
            q1 = self.df['Revenue'].quantile(0.25)
            q3 = self.df['Revenue'].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            anomalies = self.df[(self.df['Revenue'] < lower) | (self.df['Revenue'] > upper)]
            return anomalies
        return None

    def plot_top_products(self, n=5, save_path=None):
        top = self.top_selling_products(n)
        if top is not None:
            fig, ax = plt.subplots()
            top.plot(kind='bar', ax=ax, color='skyblue')
            ax.set_title('Top Selling Products')
            ax.set_ylabel('Revenue')
            if save_path:
                fig.savefig(save_path)
                plt.close(fig)
            else:
                st.pyplot(fig)

    def plot_sales_trends(self, save_path=None):
        trend = self.sales_trends()
        if trend is not None:
            fig, ax = plt.subplots()
            trend.plot(ax=ax, marker='o')
            ax.set_title('Sales Trends Over Time')
            ax.set_ylabel('Revenue')
            if save_path:
                fig.savefig(save_path)
                plt.close(fig)
            else:
                st.pyplot(fig)

    def plot_regional_performance(self, save_path=None):
        region = self.regional_performance()
        if region is not None:
            fig, ax = plt.subplots()
            region.plot(kind='bar', ax=ax, color='orange')
            ax.set_title('Regional Performance')
            ax.set_ylabel('Revenue')
            if save_path:
                fig.savefig(save_path)
                plt.close(fig)
            else:
                st.pyplot(fig)

    def plot_customer_segment(self, save_path=None):
        segment = self.customer_segment_analysis()
        if segment is not None:
            fig, ax = plt.subplots()
            segment.plot(kind='pie', ax=ax, autopct='%1.1f%%')
            ax.set_ylabel('')
            ax.set_title('Customer Segment Analysis')
            if save_path:
                fig.savefig(save_path)
                plt.close(fig)
            else:
                st.pyplot(fig)
