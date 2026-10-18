
from random import randint
import streamlit as st

st.set_page_config(
    page_title="Coin Flipper",
    page_icon="🪙",
    layout="centered"
)


def flip(num_coins, times):
    sides = 2 ** num_coins
    wins = 0
    flips = 0

    if times:
        for _ in range(times):
            result = randint(1, sides)
            flips += 1

            if result != 1:
                wins += 1

    else:
        while True:
            result = randint(1, sides)
            flips += 1

            if result == 1:
                break

            wins += 1

    return wins, flips


# App interface
st.title("🪙 Coin Flipper")
st.write("Simulate coin flips and see how many wins you get!")

num_coins = st.number_input(
    "Number of coins",
    min_value=1,
    max_value=1000,
    value=1,
    step=1
)

until_lose = st.checkbox("Until I Lose")

if until_lose:
    st.info(
        "Keep flipping until the first loss. "
        "The number of flips can vary significantly."
    )
    times = 0
else:
    times = st.number_input(
        "Number of times",
        min_value=1,
        max_value=1_000_000_000,
        value=10,
        step=1
    )

    st.caption(
        f"Each flip has a "
        f"{100 / (2 ** num_coins):.6g}% chance of losing."
    )

if st.button("Run", type="primary", use_container_width=True):
    # Warn about simulations that could take a very long time.
    if until_lose and num_coins > 20:
        st.error(
            "This simulation could take an extremely long time. "
            "With this many coins, the expected number of flips "
            "before a loss is greater than one million."
        )
    elif not until_lose and times > 10_000_000:
        st.error(
            "That is a very large simulation and may take a long "
            "time. Please use 10 million flips or fewer."
        )
    else:
        with st.spinner("Flipping..."):
            wins, total_flips = flip(int(num_coins), int(times))

        st.divider()
        st.subheader("Results")

        st.metric("Number of Wins", f"{wins:,}")

        if until_lose:
            st.metric("Total Flips", f"{total_flips:,}")
            st.success(
                f"You won {wins:,} times before your first loss!"
            )
        else:
            st.metric("Total Flips", f"{total_flips:,}")
            st.metric(
                "Win Rate",
                f"{wins / total_flips * 100:.4f}%"
            )
