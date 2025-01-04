import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt

def main():
    st.title("Time Series Chart Demo")

    # Generate sample data
    np.random.seed(42)  # For reproducibility
    dates = pd.date_range("2023-01-01", periods=30, freq="D")
    values = np.random.randn(30).cumsum()
    df = pd.DataFrame({"Date": dates, "Value": values}).set_index("Date")

    # 1. Built-in Streamlit Chart Component
    st.subheader("1. Built-in Streamlit Chart")
    st.line_chart(df)

    # 2. Matplotlib Integration
    st.subheader("2. Matplotlib")
    fig, ax = plt.subplots()
    ax.plot(df.index, df["Value"], marker="o", linestyle="-", label="Value")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.set_title("Matplotlib Time Series Chart")
    ax.legend()
    st.pyplot(fig)

    # 3. Plotly
    st.subheader("3. Plotly")
    fig_plotly = px.line(df, x=df.index, y="Value", title="Plotly Time Series Chart")
    st.plotly_chart(fig_plotly)

    # 4. Altair
    st.subheader("4. Altair")
    # Altair requires a non-indexed dataframe (use reset_index)
    df_altair = df.reset_index()
    chart = (
        alt.Chart(df_altair)
        .mark_line(point=True)
        .encode(
            x="Date:T",
            y="Value:Q",
            tooltip=["Date:T", "Value:Q"]
        )
        .properties(title="Altair Time Series Chart")
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()
