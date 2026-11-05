
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from simulation import run_simulation, compare_counters


st.set_page_config(
    page_title="Supermarket Checkout Simulation",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Supermarket Checkout Queue Simulation")

st.write(
    "A Python-based simulation to analyse customer "
    "waiting time and checkout counter performance."
)

# Sidebar settings
st.sidebar.header("Simulation Settings")

total_customers = st.sidebar.slider(
    "Total Customers", 10, 200, 50
)

num_counters = st.sidebar.slider(
    "Number of Checkout Counters", 1, 10, 3
)

avg_arrival_time = st.sidebar.slider(
    "Average Arrival Interval (minutes)",
    0.5, 10.0, 2.0, 0.5
)

avg_service_time = st.sidebar.slider(
    "Average Service Time (minutes)",
    1.0, 15.0, 5.0, 0.5
)

seed = st.sidebar.number_input(
    "Random Seed", min_value=0, value=42
)

if st.sidebar.button("Run Simulation", type="primary"):

    df, metrics, utilisation_df = run_simulation(
        total_customers,
        num_counters,
        avg_arrival_time,
        avg_service_time,
        seed
    )

    st.session_state["results"] = (
        df, metrics, utilisation_df
    )

if "results" in st.session_state:

    df, metrics, utilisation_df = st.session_state["results"]

    st.subheader("Simulation Performance")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Customers",
        metrics["Total Customers"]
    )

    col2.metric(
        "Average Waiting Time",
        f'{metrics["Average Waiting Time"]:.2f} min'
    )

    col3.metric(
        "Average Service Time",
        f'{metrics["Average Service Time"]:.2f} min'
    )

    col4.metric(
        "Average Time in System",
        f'{metrics["Average Time in System"]:.2f} min'
    )

    st.divider()

    st.subheader("Checkout Counter Utilisation")

    st.bar_chart(
        utilisation_df.set_index("Counter")
    )

    st.subheader("Customer Waiting Time")

    fig, ax = plt.subplots()

    ax.plot(
        df["Customer"],
        df["Waiting Time"],
        marker="o"
    )

    ax.set_xlabel("Customer Number")
    ax.set_ylabel("Waiting Time (minutes)")
    ax.set_title("Waiting Time of Each Customer")
    ax.grid(True)

    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Customer Service Records")

    st.dataframe(
        df,
        use_container_width=True
    )

    st.subheader("Waiting Time Distribution")

    fig2, ax2 = plt.subplots()

    ax2.hist(
        df["Waiting Time"],
        bins=10,
        edgecolor="black"
    )

    ax2.set_xlabel("Waiting Time (minutes)")
    ax2.set_ylabel("Number of Customers")
    ax2.set_title("Distribution of Customer Waiting Times")

    st.pyplot(fig2)
    plt.close(fig2)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Customer Records",
        data=csv,
        file_name="customer_records.csv",
        mime="text/csv"
    )

else:
    st.info("Adjust the settings and click Run Simulation.")
    st.divider()

st.header("📊 Checkout Counter Comparison")

st.write(
    "Compare customer waiting time with different "
    "numbers of checkout counters."
)

if st.button("Compare Counter Configurations"):

    comparison_df = compare_counters(
        total_customers,
        num_counters,
        avg_arrival_time,
        avg_service_time,
        seed
    )

    st.subheader("Comparison Table")
    st.dataframe(comparison_df, use_container_width=True)

    st.subheader("Average Waiting Time Comparison")

    chart_data = comparison_df.set_index(
        "Number of Counters"
    )

    st.line_chart(
        chart_data["Average Waiting Time"]
    )
