# xbbg - Intuitive Bloomberg API Documentation

*Last Updated: September 21, 2025*
*Source: GitHub Repository (alpha-xone/xbbg) and PyPI*

## Overview

xbbg is a Python library that provides an intuitive and user-friendly wrapper around the Bloomberg API. It simplifies Bloomberg data retrieval with Excel-compatible inputs and straightforward data access patterns.

**Current Version**: 0.7.7 (Released June 19, 2022)
**License**: Apache Software License
**Repository**: https://github.com/alpha-xone/xbbg

## Key Features

- **Excel Compatible Inputs**: Familiar syntax for Bloomberg users
- **Straightforward Intraday Bar Requests**: Simplified intraday data access
- **Data Subscriptions**: Real-time data streaming capabilities
- **Comprehensive Data Coverage**: Reference, historical, intraday, and tick data
- **Local Data Storage**: Optional local caching with compliance features
- **Pandas Integration**: Returns data as pandas DataFrames

## Installation

### Prerequisites

1. **Bloomberg C++ SDK**: Version 3.12.1 or higher
2. **Bloomberg Official Python API** (blpapi)
3. **Python Dependencies**: numpy, pandas, ruamel.yaml, pyarrow

### Installation Command

```bash
pip install xbbg
```

### Python Version Support

- Python 3.6
- Python 3.7
- Python 3.8

### Bloomberg API Setup

For Bloomberg API integration, you need to:
1. Copy `blpapi3_32.dll` and `blpapi3_64.dll` to the Bloomberg BLPAPI_ROOT folder
2. Usually located in `blp/DAPI` directory
3. Ensure Bloomberg Terminal is running and logged in

## Core Functions

### 1. bdp() - Reference Data

Retrieves current/static reference data points.

```python
from xbbg import blp

# Single ticker, single field
data = blp.bdp('AAPL US Equity', 'PX_LAST')

# Multiple tickers and fields
data = blp.bdp(
    tickers=['AAPL US Equity', 'MSFT US Equity'],
    flds=['PX_LAST', 'MARKET_CAP', 'PE_RATIO']
)

# With Bloomberg overrides
data = blp.bdp(
    tickers='NVDA US Equity',
    flds=['Security_Name', 'GICS_Sector_Name'],
    DVD_Hist_Start_Dt='20200101'
)
```

**Parameters**:
- `tickers`: String or list of Bloomberg tickers
- `flds`: String or list of Bloomberg fields
- `**kwargs`: Bloomberg overrides and parameters

**Returns**: pandas.DataFrame

### 2. bdh() - Historical Data

Retrieves historical time series data.

```python
# Basic historical data
data = blp.bdh(
    tickers='SPX Index',
    flds=['PX_HIGH', 'PX_LOW', 'PX_LAST'],
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# Multiple tickers
data = blp.bdh(
    tickers=['AAPL US Equity', 'GOOGL US Equity'],
    flds='PX_LAST',
    start_date='2023-01-01'
)

# With dividend adjustments
data = blp.bdh(
    tickers='AAPL US Equity',
    flds='PX_LAST',
    start_date='2023-01-01',
    adjust='dividend'
)
```

**Parameters**:
- `tickers`: String or list of Bloomberg tickers
- `flds`: String or list of fields (default: 'PX_LAST')
- `start_date`: Start date for data range
- `end_date`: End date (default: 'today')
- `adjust`: Adjustment type ('dividend', 'split', 'all', None)
- `**kwargs`: Additional Bloomberg parameters

**Returns**: pandas.DataFrame with DatetimeIndex

### 3. bds() - Block/Static Data

Retrieves block data sets and static bulk data.

```python
# Corporate actions
data = blp.bds('AAPL US Equity', 'DVD_Hist_All')

# Index members
data = blp.bds('SPX Index', 'INDX_MEMBERS')

# Using portfolio data request
data = blp.bds(
    tickers='portfolio_name',
    flds='PORTFOLIO_DATA',
    use_port=True
)
```

**Parameters**:
- `tickers`: String or list of Bloomberg tickers
- `flds`: String or list of Bloomberg fields
- `use_port`: Boolean, use PortfolioDataRequest if True
- `**kwargs`: Bloomberg overrides

**Returns**: pandas.DataFrame

### 4. bdib() - Intraday Bar Data

Retrieves intraday bar/OHLCV data.

```python
# Basic intraday bars
data = blp.bdib(
    ticker='AAPL US Equity',
    dt='2023-12-15'
)

# Specific session and data type
data = blp.bdib(
    ticker='ES1 Index',
    dt='2023-12-15',
    session='day',
    typ='TRADE'
)

# Custom time interval
data = blp.bdib(
    ticker='EURUSD Curncy',
    dt='2023-12-15',
    interval=60  # 60-minute bars
)
```

**Parameters**:
- `ticker`: Bloomberg ticker (single ticker only)
- `dt`: Date to download (string or datetime)
- `session`: Trading session ('allday', 'day', 'premarket', 'postmarket')
- `typ`: Data type ('TRADE', 'BID', 'ASK', 'BEST_BID', 'BEST_ASK')
- `interval`: Bar interval in minutes
- `**kwargs`: Additional parameters

**Returns**: pandas.DataFrame with datetime index

### 5. bdtick() - Tick Data

Retrieves tick-by-tick data.

```python
# All tick data for a day
data = blp.bdtick(
    ticker='AAPL US Equity',
    dt='2023-12-15'
)

# Specific time range
data = blp.bdtick(
    ticker='ES1 Index',
    dt='2023-12-15',
    time_range=('09:30', '16:00')
)

# Specific tick types
data = blp.bdtick(
    ticker='EURUSD Curncy',
    dt='2023-12-15',
    types=['TRADE', 'BID', 'ASK']
)
```

**Parameters**:
- `ticker`: Bloomberg ticker (single ticker only)
- `dt`: Date to download
- `session`: Trading session type
- `time_range`: Tuple of (start_time, end_time)
- `types`: List of tick event types
- `**kwargs`: Additional parameters

**Returns**: pandas.DataFrame

### 6. earning() - Earnings Data

Retrieves corporate earnings data.

```python
# Revenue by geography
data = blp.earning(
    ticker='AAPL US Equity',
    by='Geo',
    typ='Revenue'
)

# Earnings by product
data = blp.earning(
    ticker='GOOGL US Equity',
    by='Product',
    typ='Operating_Income'
)
```

**Parameters**:
- `ticker`: Bloomberg ticker
- `by`: Breakdown type ('Geo', 'Product', 'Business')
- `typ`: Data type ('Revenue', 'Operating_Income', etc.)
- `ccy`: Currency override
- `level`: Detail level
- `**kwargs**: Additional parameters

**Returns**: pandas.DataFrame

### 7. dividend() - Dividend Data

Retrieves dividend information.

```python
# Historical dividends
data = blp.dividend('AAPL US Equity')

# Dividends with date range
data = blp.dividend(
    ticker='MSFT US Equity',
    start_date='2023-01-01',
    end_date='2023-12-31'
)
```

**Parameters**:
- `ticker`: Bloomberg ticker
- `start_date`: Start date for dividend history
- `end_date`: End date for dividend history
- `**kwargs`: Additional parameters

**Returns**: pandas.DataFrame

## Advanced Features

### Data Adjustments

xbbg supports various data adjustments for historical data:

```python
# Dividend adjustment
data = blp.bdh('AAPL US Equity', 'PX_LAST', adjust='dividend')

# Split adjustment
data = blp.bdh('AAPL US Equity', 'PX_LAST', adjust='split')

# Both dividends and splits
data = blp.bdh('AAPL US Equity', 'PX_LAST', adjust='all')
```

### Currency Adjustment

```python
from xbbg import blp

# Adjust prices to different currency
data = blp.adjust_ccy(
    data=price_data,
    tickers='AAPL US Equity',
    ccy='EUR'
)
```

### Turnover Calculations

```python
# Calculate turnover metrics
data = blp.turnover(
    ticker='AAPL US Equity',
    dt='2023-12-15'
)
```

### Data Subscriptions

```python
# Real-time data subscription
data = blp.subscribe(
    tickers=['AAPL US Equity', 'MSFT US Equity'],
    flds=['PX_LAST', 'BID', 'ASK']
)

# Live data streaming
data = blp.live(
    tickers='SPX Index',
    flds='PX_LAST'
)
```

## Data Storage and Compliance

### Local Data Storage

Set the `BBG_ROOT` environment variable to enable local data caching:

```python
import os
os.environ['BBG_ROOT'] = '/path/to/local/storage'
```

### Compliance Requirements

**Important**: Local data usage must comply with the Bloomberg Datafeed Addendum:
- Data "cannot leave the local PC you use to access the BLOOMBERG PROFESSIONAL service"
- Ensure proper data governance and access controls
- Local storage is preferred over Bloomberg for all queries by default when configured

## Error Handling

```python
from xbbg import blp
import pandas as pd

try:
    data = blp.bdp('INVALID_TICKER', 'PX_LAST')
except Exception as e:
    print(f"Error retrieving data: {e}")
    data = pd.DataFrame()  # Return empty DataFrame
```

## Best Practices

### Performance Optimization

1. **Batch Requests**: Request multiple tickers/fields in single calls
2. **Field Selection**: Only request necessary fields
3. **Date Ranges**: Use appropriate date ranges for historical data
4. **Local Caching**: Utilize local storage for frequently accessed data

### Common Patterns

```python
# Standard equity data retrieval
def get_equity_data(tickers, start_date, end_date):
    return blp.bdh(
        tickers=tickers,
        flds=['PX_OPEN', 'PX_HIGH', 'PX_LOW', 'PX_LAST', 'PX_VOLUME'],
        start_date=start_date,
        end_date=end_date
    )

# Reference data with error handling
def get_reference_data(tickers, fields):
    try:
        return blp.bdp(tickers=tickers, flds=fields)
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()
```

## Configuration Options

### Bloomberg Overrides

Common Bloomberg overrides can be passed as keyword arguments:

```python
# Currency override
data = blp.bdp('AAPL US Equity', 'PX_LAST', CRNCY='EUR')

# Date overrides
data = blp.bds('AAPL US Equity', 'DVD_Hist_All', DVD_Start_Dt='20200101')

# Pricing source
data = blp.bdh('AAPL US Equity', 'PX_LAST', pricing_source='BGN')
```

### Session Configuration

```python
# Configure Bloomberg session options
import blpapi

session_options = blpapi.SessionOptions()
session_options.setServerHost('localhost')
session_options.setServerPort(8194)
```

## Comparison with Official BLPAPI

| Feature | xbbg | Official BLPAPI |
|---------|------|-----------------|
| **Ease of Use** | Simple, pythonic | Complex, verbose |
| **Return Format** | pandas DataFrames | Native Bloomberg objects |
| **Error Handling** | Built-in | Manual implementation |
| **Data Adjustments** | Automatic options | Manual calculations |
| **Excel Compatibility** | Native support | Requires conversion |
| **Learning Curve** | Minimal | Steep |

## Common Use Cases

### Portfolio Analysis

```python
# Get portfolio holdings data
holdings = blp.bdp(
    tickers=['AAPL US Equity', 'MSFT US Equity', 'GOOGL US Equity'],
    flds=['PX_LAST', 'MARKET_CAP', 'PE_RATIO', 'BETA']
)

# Historical performance
performance = blp.bdh(
    tickers=['AAPL US Equity', 'MSFT US Equity'],
    flds='PX_LAST',
    start_date='2023-01-01'
)
```

### Risk Management

```python
# Get volatility data
vol_data = blp.bdp(
    tickers='SPX Index',
    flds=['VOLATILITY_30D', 'VOLATILITY_90D', 'VOLATILITY_260D']
)

# Historical volatility
hist_vol = blp.bdh(
    tickers='VIX Index',
    flds='PX_LAST',
    start_date='2023-01-01'
)
```

### Market Research

```python
# Sector analysis
sector_data = blp.bdp(
    tickers=['XLK US Equity', 'XLF US Equity', 'XLE US Equity'],
    flds=['PX_LAST', 'CHG_PCT_1D', 'CHG_PCT_YTD']
)

# Economic indicators
econ_data = blp.bdh(
    tickers=['USGG10YR Index', 'DXY Curncy', 'CL1 Comdty'],
    flds='PX_LAST',
    start_date='2023-01-01'
)
```

## Troubleshooting

### Common Issues

1. **Bloomberg Terminal Not Running**
   - Ensure Bloomberg Terminal is launched and logged in
   - Check Bloomberg service status

2. **DLL Files Missing**
   - Copy `blpapi3_32.dll` and `blpapi3_64.dll` to BLPAPI_ROOT
   - Verify Bloomberg C++ SDK installation

3. **Data Not Available**
   - Check ticker validity
   - Verify field names
   - Confirm data permissions

4. **Timeout Errors**
   - Increase timeout parameters
   - Reduce request size
   - Check network connectivity

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use timeout parameters
data = blp.bdh(
    tickers='AAPL US Equity',
    flds='PX_LAST',
    timeout=60000  # 60 seconds
)
```

## Version History

- **0.7.7** (June 2022): Latest stable release
- **0.7.0**: Added bdh column order preservation, timeout arguments
- **0.6.0**: Speed improvements, tick data availability

## Resources

- **GitHub Repository**: https://github.com/alpha-xone/xbbg
- **PyPI Package**: https://pypi.org/project/xbbg/
- **Bloomberg API Documentation**: https://bloomberg.github.io/blpapi-docs/
- **Example Notebooks**: Available in GitHub repository

---

*xbbg provides an intuitive interface to Bloomberg's comprehensive financial data, making it accessible to Python developers without the complexity of the underlying Bloomberg API.*