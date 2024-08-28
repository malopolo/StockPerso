import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import ssl

# Bypass SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal

# Fetch NVIDIA stock data
ticker = 'NVDA'
data = yf.download(ticker, period='1y')

# Calculate Moving Averages
data['50EMA'] = data['Close'].ewm(span=50, adjust=False).mean()
data['200EMA'] = data['Close'].ewm(span=200, adjust=False).mean()

# Calculate RSI
data['RSI'] = calculate_rsi(data)

# Calculate MACD
data['MACD'], data['Signal'] = calculate_macd(data)

# Generate buy/sell signals
data['Buy_Signal'] = ((data['50EMA'] > data['200EMA']) & (data['RSI'] < 30))
data['Sell_Signal'] = ((data['50EMA'] < data['200EMA']) & (data['RSI'] > 70))

# Create subplots with shared x-axis
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                    specs=[[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}]])

# Stock price plot
fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='NVDA Close Price', line=dict(color='blue')), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['50EMA'], mode='lines', name='50EMA', line=dict(color='orange')), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['200EMA'], mode='lines', name='200EMA', line=dict(color='green')), row=1, col=1)

# Buy signals
fig.add_trace(go.Scatter(x=data[data['Buy_Signal']].index, y=data['50EMA'][data['Buy_Signal']], mode='markers', name='Buy Signal', marker=dict(color='green', symbol='triangle-up', size=10)), row=1, col=1)

# Sell signals
fig.add_trace(go.Scatter(x=data[data['Sell_Signal']].index, y=data['50EMA'][data['Sell_Signal']], mode='markers', name='Sell Signal', marker=dict(color='red', symbol='triangle-down', size=10)), row=1, col=1)

# RSI plot
fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='orange')), row=2, col=1)
fig.add_shape(type="line", x0=data.index.min(), y0=70, x1=data.index.max(), y1=70, line=dict(color="red"), row=2, col=1)
fig.add_shape(type="line", x0=data.index.min(), y0=30, x1=data.index.max(), y1=30, line=dict(color="green"), row=2, col=1)

# MACD plot
fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')), row=3, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['Signal'], mode='lines', name='Signal Line', line=dict(color='orange')), row=3, col=1)
fig.add_trace(go.Bar(x=data.index, y=data['MACD'] - data['Signal'], name='MACD Histogram', marker=dict(color='gray')), row=3, col=1)

# Layout
fig.update_layout(
    title=f'{ticker} Stock Price with Buy/Sell Signals, RSI, and MACD',
    xaxis_title='Date',
    yaxis_title='Price',
    yaxis2_title='RSI',
    yaxis3_title='MACD',
    height=800,
    xaxis_rangeslider_visible=False
)

# Enable scroll zoom
fig.update_layout(
    xaxis=dict(
        rangeslider=dict(
            visible=False
        ),
        type="date"
    ),
    xaxis2=dict(
        type="date"
    ),
    xaxis3=dict(
        type="date"
    )
)

fig.update_xaxes(rangeslider_visible=False)
fig.update_layout(dragmode='zoom', hovermode="x unified")

# Display the plot
fig.show()
