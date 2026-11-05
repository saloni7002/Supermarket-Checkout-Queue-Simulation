
import simpy
import numpy as np
import pandas as pd


def run_simulation(
    total_customers=50,
    num_counters=3,
    avg_arrival_time=2.0,
    avg_service_time=5.0,
    seed=42
):
    # Set random seed for reproducible results
    rng = np.random.default_rng(seed)

    # Create simulation environment
    env = simpy.Environment()

    
    # Create checkout counters
    counters = simpy.Resource(
        env,
        capacity=num_counters
    )

    # Create counter identification system
    counter_ids = simpy.Store(
        env,
        capacity=num_counters
    )

    # Assign IDs to all checkout counters
    for counter_id in range(num_counters):
        counter_ids.put(counter_id)


    customer_records = []
    counter_busy_time = [0.0] * num_counters

    def customer_process(customer_id, arrival_time):
        # Wait until customer arrival
        yield env.timeout(arrival_time - env.now)

        actual_arrival = env.now

        # Request a checkout counter
        with counters.request() as request:
            yield request

            service_start = env.now
            waiting_time = service_start - actual_arrival

            # Generate service time
            service_time = rng.exponential(
                avg_service_time
            )

            # Identify the actual checkout counter
            counter_id = yield counter_ids.get()

            # Serve customer
            yield env.timeout(service_time)

            departure_time = env.now

            counter_busy_time[counter_id] += service_time
            yield counter_ids.put(counter_id)

            customer_records.append({
                "Customer": customer_id,
                "Arrival Time": round(actual_arrival, 2),
                "Service Start": round(service_start, 2),
                "Service Time": round(service_time, 2),
                "Waiting Time": round(waiting_time, 2),
                "Departure Time": round(departure_time, 2),
                "Counter": counter_id + 1
            })

    # Generate customer arrival times
    arrival_times = []
    current_time = 0.0

    for _ in range(total_customers):
        current_time += rng.exponential(
            avg_arrival_time
        )
        arrival_times.append(current_time)

    # Schedule all customer processes
    for i, arrival_time in enumerate(arrival_times):
        env.process(
            customer_process(i + 1, arrival_time)
        )

    # Run the simulation
    env.run()

    # Convert records into DataFrame
    df = pd.DataFrame(customer_records)

    if not df.empty:
        df = df.sort_values(
            by="Customer"
        ).reset_index(drop=True)

    if df.empty:
        return df, {}, pd.DataFrame()

    # Calculate performance metrics
    metrics = {
        "Total Customers": len(df),
        "Customers Served": len(df),
        "Average Waiting Time": df["Waiting Time"].mean(),
        "Maximum Waiting Time": df["Waiting Time"].max(),
        "Average Service Time": df["Service Time"].mean(),
        "Average Time in System": (
            df["Departure Time"] - df["Arrival Time"]
        ).mean(),
        "Total Simulation Time": df["Departure Time"].max()
    }

    # Counter utilisation
    utilisation_records = []

    for i, busy_time in enumerate(counter_busy_time):
        utilisation = (
            busy_time / metrics["Total Simulation Time"]
        ) * 100

        utilisation_records.append({
            "Counter": f"Counter {i + 1}",
            "Utilisation (%)": round(utilisation, 2)
        })

    utilisation_df = pd.DataFrame(
        utilisation_records
    )

    return df, metrics, utilisation_df
def compare_counters(
    total_customers,
    max_counters,
    avg_arrival_time,
    avg_service_time,
    seed
):
    comparison = []

    for counters in range(1, max_counters + 1):

        df, metrics, utilisation_df = run_simulation(
            total_customers,
            counters,
            avg_arrival_time,
            avg_service_time,
            seed
        )

        comparison.append({
            "Number of Counters": counters,
            "Average Waiting Time": round(
                metrics["Average Waiting Time"], 2
            ),
            "Average Service Time": round(
                metrics["Average Service Time"], 2
            ),
            "Average Time in System": round(
                metrics["Average Time in System"], 2
            )
        })

    return pd.DataFrame(comparison)
