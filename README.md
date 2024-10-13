# DivStripper+

DivStripper+ is a tool that helps in identifying profitable dividend stripping opportunities by analyzing historical dividend announcements and stock price data. It scrapes financial data, processes it, and generates visual insights on stock prices around dividend announcement and ex-dividend dates.

## Features
- **Dividend Data Scraping**: Retrieves dividend announcements from BSE India and MoneyControl.
- **Price Data Scraping**: Fetches historical stock prices from BSE India.
- **Levenshtein Search**: Implements Damerau-Levenshtein distance to find the closest matching stock based on user input.
- **Data Visualization**: Generates charts showing stock prices around key dates (announcement and ex-dividend) to visualize the impact of dividend announcements.
- **CSV Support**: Reads and writes data to CSV files to store price data for further analysis.
  
## Requirements
- Python 3.x
- Required libraries: `requests`, `pandas`, `matplotlib`, `BeautifulSoup`, `re`, `fastDamerauLevenshtein`, `enchant`, `Flask`

## Usage

1. Clone the repository.
2. Install the required packages:
    ```
    pip install -r requirements.txt
    ```
3. Run the script:
    ```
    python divstripper.py
    ```
4. Enter the company name (from Sensex) to look up its dividend history and stock performance.

## Functions
- `get_dividend_data()`: Fetches dividend data for a given scrip from BSE India.
- `get_prices()`: Retrieves historical price data for a given scrip from BSE India.
- `prepare_all_charts()`: Generates stock price charts with key dividend-related dates (announcement, ex-dividend) marked.
  
## Example
Once you run the script, you will be prompted to enter a company name from Sensex. The program will match the closest company using Levenshtein distance, fetch the corresponding data, and display a chart showing stock prices around the dividend announcement and ex-dividend dates.

## File Structure
- **Sensex.csv**: Contains a list of companies and their corresponding stock codes.
- **Previous_Announcements.csv**: Stores previously fetched dividend announcements for faster lookups.

## License
This project is licensed under the MIT License.

## Author
Hitansh Shah

