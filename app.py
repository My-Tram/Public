import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Realtime Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

st.sidebar.title("⚙️ Dashboard")

ticker = st.sidebar.selectbox(
    "Ticker",
    ["AAPL", "MSFT", "NVDA"]
)

st.sidebar.markdown("---")
st.sidebar.success("● LIVE")
st.sidebar.write("1 second = 1 candle")
st.sidebar.write("60 FPS smooth animation")

st.title("📈 Realtime Trading Dashboard")
st.caption(f"{ticker} • Smooth realtime simulation")

html_code = """
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>

<style>

html, body {
    margin: 0;
    padding: 0;
    background: #0e1117;
    overflow: hidden;
}

#container {
    position: relative;
    width: 100%;
    height: 650px;
}

#chart {
    width: 100%;
    height: 650px;
}

#status {
    position: absolute;
    top: 12px;
    left: 15px;
    z-index: 100;

    color: #00ff88;
    background: rgba(0,0,0,0.55);

    padding: 6px 10px;
    border-radius: 5px;

    font-family: Arial;
    font-size: 14px;
}

#price {
    position: absolute;
    top: 48px;
    left: 15px;

    z-index: 100;

    color: white;

    font-family: Arial;
    font-size: 24px;
    font-weight: bold;
}

#timer {
    position: absolute;
    top: 85px;
    left: 15px;

    z-index: 100;

    color: #aaaaaa;

    font-family: Arial;
    font-size: 13px;
}

</style>

</head>

<body>

<div id="container">

    <div id="status">● LIVE</div>

    <div id="price">--</div>

    <div id="timer">
        New candle in 1.0s
    </div>

    <div id="chart"></div>

</div>

<script>

if (typeof LightweightCharts === "undefined") {

    document.getElementById("status").innerText =
        "❌ Chart library not loaded";

}
else {

    const container = document.getElementById("chart");

    const chart = LightweightCharts.createChart(
        container,
        {
            width: container.clientWidth,
            height: 650,

            layout: {
                background: {
                    color: "#0e1117"
                },
                textColor: "#d1d4dc"
            },

            grid: {
                vertLines: {
                    color: "#1e222d"
                },

                horzLines: {
                    color: "#1e222d"
                }
            },

            rightPriceScale: {
                borderColor: "#2a2e39"
            },

            timeScale: {

                borderColor: "#2a2e39",

                timeVisible: true,

                secondsVisible: true,

                rightOffset: 5,

                barSpacing: 8

            },

            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal
            }
        }
    );


    // =========================
    // CANDLE
    // =========================

    const candleSeries = chart.addSeries(
        LightweightCharts.CandlestickSeries,
        {

            upColor: "#26a69a",

            downColor: "#ef5350",

            borderUpColor: "#26a69a",

            borderDownColor: "#ef5350",

            wickUpColor: "#26a69a",

            wickDownColor: "#ef5350"

        }
    );


    // =========================
    // MA
    // =========================

    const maSeries = chart.addSeries(
        LightweightCharts.LineSeries,
        {

            color: "#2962FF",

            lineWidth: 2

        }
    );


    // =========================
    // VOLUME
    // =========================

    const volumeSeries = chart.addSeries(
        LightweightCharts.HistogramSeries,
        {

            priceFormat: {
                type: "volume"
            },

            priceScaleId: "",

            scaleMargins: {

                top: 0.80,

                bottom: 0

            }

        }
    );


    // =========================
    // INITIAL DATA
    // =========================

    let candles = [];

    let price = 180;

    const now = Math.floor(Date.now() / 1000);


    for (let i = 60; i >= 0; i--) {

        const time = now - i;

        const open = price;

        const movement =
            (Math.random() - 0.5) * 1.5;

        const close =
            open + movement;

        const high =
            Math.max(open, close)
            + Math.random() * 0.5;

        const low =
            Math.min(open, close)
            - Math.random() * 0.5;


        candles.push({

            time: time,

            open: open,

            high: high,

            low: low,

            close: close

        });


        price = close;

    }


    candleSeries.setData(candles);


    // =========================
    // MA FUNCTION
    // =========================

    function calculateMA(data, period) {

        const result = [];

        if (data.length < period) {

            return result;

        }


        let sum = 0;


        // Initial sum

        for (
            let i = 0;
            i < period;
            i++
        ) {

            sum += data[i].close;

        }


        result.push({

            time: data[period - 1].time,

            value: sum / period

        });


        // Sliding window

        for (
            let i = period;
            i < data.length;
            i++
        ) {

            sum -= data[i - period].close;

            sum += data[i].close;


            result.push({

                time: data[i].time,

                value: sum / period

            });

        }


        return result;

    }


    maSeries.setData(
        calculateMA(candles, 9)
    );


    // =========================
    // VOLUME
    // =========================

    volumeSeries.setData(

        candles.map(function(c) {

            return {

                time: c.time,

                value:
                    1000000
                    +
                    Math.random() * 5000000,

                color:
                    c.close >= c.open
                    ? "#26a69a"
                    : "#ef5350"

            };

        })

    );


    // =========================
    // REALTIME VARIABLES
    // =========================

    let currentPrice =
        candles[candles.length - 1].close;


    let targetPrice =
        currentPrice;


    let candleStart =
        performance.now();


    const candleDuration = 1000;


    let lastTargetUpdate =
        performance.now();


    let lastMAUpdate =
        performance.now();


    let lastDisplayUpdate =
        performance.now();


    // =========================
    // NEW TARGET PRICE
    // =========================

    function generateTargetPrice() {

        const movement =
            (Math.random() - 0.5) * 1.2;


        targetPrice =
            currentPrice + movement;

    }


    // =========================
    // SMOOTH LOOP
    // =========================

    function realtimeLoop(timestamp) {


        // --------------------------------
        // Generate new target every 150ms
        // --------------------------------

        if (
            timestamp - lastTargetUpdate
            >= 150
        ) {

            generateTargetPrice();

            lastTargetUpdate =
                timestamp;

        }


        // --------------------------------
        // Smooth interpolation
        // --------------------------------

        const difference =
            targetPrice - currentPrice;


        currentPrice +=
            difference * 0.08;


        // --------------------------------
        // Current candle
        // --------------------------------

        let currentCandle =
            candles[candles.length - 1];


        currentCandle.close =
            currentPrice;


        currentCandle.high =
            Math.max(
                currentCandle.high,
                currentPrice
            );


        currentCandle.low =
            Math.min(
                currentCandle.low,
                currentPrice
            );


        // --------------------------------
        // Update candle
        // --------------------------------

        candleSeries.update(
            currentCandle
        );


        // --------------------------------
        // Update price display
        // --------------------------------

        if (
            timestamp - lastDisplayUpdate
            >= 50
        ) {

            document.getElementById(
                "price"
            ).innerText =
                "$" +
                currentPrice.toFixed(2);


            lastDisplayUpdate =
                timestamp;

        }


        // --------------------------------
        // MA only update every 150ms
        // --------------------------------

        if (
            timestamp - lastMAUpdate
            >= 150
        ) {

            const last9 =
                candles.slice(-9);


            if (last9.length === 9) {

                let sum = 0;


                for (
                    let i = 0;
                    i < last9.length;
                    i++
                ) {

                    sum +=
                        last9[i].close;

                }


                const ma =
                    sum / 9;


                maSeries.update({

                    time:
                        currentCandle.time,

                    value: ma

                });

            }


            lastMAUpdate =
                timestamp;

        }


        // --------------------------------
        // Timer
        // --------------------------------

        const elapsed =
            timestamp - candleStart;


        const remaining =
            Math.max(
                0,
                1000 - elapsed
            );


        document.getElementById(
            "timer"
        ).innerText =
            "New candle in "
            +
            (remaining / 1000)
                .toFixed(1)
            +
            "s";


        // --------------------------------
        // New candle every 1 second
        // --------------------------------

        if (
            elapsed >= candleDuration
        ) {

            const newTime =
                currentCandle.time + 1;


            const newCandle = {

                time: newTime,

                open: currentPrice,

                high: currentPrice,

                low: currentPrice,

                close: currentPrice

            };


            candles.push(
                newCandle
            );


            candleSeries.update(
                newCandle
            );


            volumeSeries.update({

                time: newTime,

                value:
                    1000000
                    +
                    Math.random() * 5000000,

                color:
                    "#26a69a"

            });


            candleStart =
                timestamp;

        }


        // --------------------------------
        // Smooth auto scroll
        // --------------------------------

        chart.timeScale()
            .scrollToRealTime();


        // --------------------------------
        // Next frame
        // --------------------------------

        requestAnimationFrame(
            realtimeLoop
        );

    }


    // START

    requestAnimationFrame(
        realtimeLoop
    );


    // =========================
    // RESIZE
    // =========================

    window.addEventListener(
        "resize",
        function() {

            chart.applyOptions({

                width:
                    container.clientWidth

            });

        }
    );


    chart.timeScale()
        .fitContent();

}

</script>

</body>

</html>
"""


components.html(
    html_code,
    height=670,
    scrolling=False
)