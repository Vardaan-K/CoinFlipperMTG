
from random import randint
import time

import streamlit as st

st.set_page_config(
    page_title="Coin Flipper",
    page_icon="🪙",
    layout="centered"
)

# One full toss cycle. A small simulation finishes in microseconds, so
# without this the coin would be created and destroyed in the same
# frame and never actually paint.
MIN_ANIMATION_SECONDS = 1.2

ANIMATION_HEIGHT = 210

# Rendered in an iframe rather than with st.markdown or st.html:
# Streamlit sanitizes those through DOMPurify, which strips the
# @keyframes rules this animation depends on.
COIN_ANIMATION = """
<!DOCTYPE html>
<html>
<head>
<style>
html, body {
    margin: 0;
    padding: 0;
    background: transparent;
    overflow: hidden;
}
.coin-stage {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    height: 200px;
    perspective: 800px;
    font-family: "Source Sans Pro", -apple-system, sans-serif;
}
.coin-toss {
    transform-style: preserve-3d;
    animation: coin-toss 1s ease-in-out infinite;
}
.coin {
    position: relative;
    width: 86px;
    height: 86px;
    transform-style: preserve-3d;
    animation: coin-spin 1s linear infinite;
}
.coin-face {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    border: 4px solid #b07d12;
    background: radial-gradient(
        circle at 32% 28%,
        #ffeb99 0%,
        #f5c330 45%,
        #c8901b 100%
    );
    box-shadow: inset 0 0 0 6px rgba(255, 255, 255, 0.28);
    color: #7a5406;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 38px;
    font-weight: 700;
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
}
.coin-tails {
    transform: rotateX(180deg);
}
.coin-shadow {
    width: 72px;
    height: 10px;
    margin-top: 10px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.35);
    filter: blur(3px);
    animation: coin-shadow 1s ease-in-out infinite;
}
.coin-caption {
    margin-top: 12px;
    color: #888;
    font-size: 0.9rem;
}
@-webkit-keyframes coin-spin {
    from { -webkit-transform: rotateX(0deg); }
    to   { -webkit-transform: rotateX(720deg); }
}
@keyframes coin-spin {
    from { transform: rotateX(0deg); }
    to   { transform: rotateX(720deg); }
}
@keyframes coin-toss {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-72px); }
}
@keyframes coin-shadow {
    0%, 100% { transform: scale(1); opacity: 0.35; }
    50%      { transform: scale(0.6); opacity: 0.12; }
}
</style>
</head>
<body>
<div class="coin-stage">
  <div class="coin-toss">
    <div class="coin">
      <div class="coin-face coin-heads">H</div>
      <div class="coin-face coin-tails">T</div>
    </div>
  </div>
  <div class="coin-shadow"></div>
  <div class="coin-caption">Flipping...</div>
</div>
</body>
</html>
"""


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


def flip_with_animation(num_coins, times):
    """Run the simulation while a cartoon coin spins on screen."""
    animation = st.empty()

    animation.iframe(COIN_ANIMATION, height=ANIMATION_HEIGHT)

    start = time.perf_counter()
    try:
        wins, flips = flip(num_coins, times)
        remaining = MIN_ANIMATION_SECONDS - (time.perf_counter() - start)

        if remaining > 0:
            time.sleep(remaining)
    finally:
        animation.empty()

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
        wins, total_flips = flip_with_animation(int(num_coins), int(times))

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
