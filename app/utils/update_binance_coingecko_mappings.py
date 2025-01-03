import os
import requests
from dotenv import load_dotenv
from pycoingecko import CoinGeckoAPI
from sqlalchemy import create_engine, Column, String, Index
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load environment variables from the .env file
# Load environment variables from the specified .env file
load_dotenv(dotenv_path=".env.micro.central")

# Access the environment variables
host = os.getenv("HOST")
database = os.getenv("DATABASE")
user = os.getenv("USR")
password = os.getenv("PASSWD")

# Database setup (replace with your database connection details)
DATABASE_URL = f"postgresql://{user}:{password}@{host}:5432/{database}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class BinanceCoinGeckoMapping(Base):
    __tablename__ = 'binance_coingecko_mapping'
    binance_symbol = Column(String, primary_key=True)
    coingecko_id = Column(String, nullable=False)

    # Create an index on the binance_symbol column
    __table_args__ = (
        Index('ix_binance_symbol', 'binance_symbol'),
    )

Base.metadata.create_all(engine)

# Direct mappings for well-known tokens
direct_mappings = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'BNB': 'binancecoin',
    'LUNC': 'terra-luna',
    'NEAR': 'near',
    'ADA': 'cardano',
    'SOL': 'solana',
    'DOT': 'polkadot',
    'DOGE': 'dogecoin',
    'LTC': 'litecoin',
    'MATIC': 'matic-network',
    'AVAX': 'avalanche-2',
    'LINK': 'chainlink',
    'XLM': 'stellar',
    'ATOM': 'cosmos',
    'ALGO': 'algorand',
    'VET': 'vechain',
    'FIL': 'filecoin',
    'TRX': 'tron',
    'EOS': 'eos',
    'AAVE': 'aave',
    'UNI': 'uniswap',
    'SUSHI': 'sushi',
    'YFI': 'yearn-finance',
    'COMP': 'compound-coin',
    'SNX': 'synthetix-network-token',
    'MKR': 'maker',
    'CAKE': 'pancakeswap-token',
    'ICP': 'internet-computer',
    'THETA': 'theta-token',
    'XTZ': 'tezos',
    'NEO': 'neo',
    'KSM': 'kusama',
    'ZIL': 'zilliqa',
    'ZRX': '0x',
    'ENJ': 'enjincoin',
    'MANA': 'decentraland',
    'SAND': 'the-sandbox',
    'AXS': 'axie-infinity',
    'GRT': 'the-graph',
    'CHZ': 'chiliz',
    'RUNE': 'thorchain',
    'FTT': 'ftx-token',
    'HBAR': 'hedera-hashgraph',
    '1INCH': '1inch',
    'LRC': 'loopring',
    'GALA': 'gala',
    'BAT': 'basic-attention-token',
    'ANKR': 'ankr',
    'CELR': 'celer-network',
    'HOT': 'holo',
    'OCEAN': 'ocean-protocol',
    'BAND': 'band-protocol',
    'RSR': 'reserve-rights-token',
    'BAL': 'balancer',
    'REN': 'ren',
    'KAVA': 'kava',
    'CELO': 'celo',
    'DGB': 'digibyte',
    'CTSI': 'cartesi',
    'STMX': 'stormx',
    'OGN': 'origin-protocol',
    'AR': 'arweave',
    'ALICE': 'myneighboralice',
    'COTI': 'coti',
    'SRM': 'serum',
    'CRV': 'curve-dao-token',
    'UMA': 'uma',
    'SXP': 'swipe',
    'INJ': 'injective-protocol',
    'KNC': 'kyber-network-crystal',
    'BNT': 'bancor',
    'GNO': 'gnosis',
    'ENS': 'ethereum-name-service',
    'QNT': 'quant-network',
    'FLOW': 'flow',
    'MINA': 'mina-protocol',
    'ROSE': 'oasis-network',
    'STORJ': 'storj',
    'MTL': 'metal',
    'MIR': 'mirror-protocol',
    'TWT': 'trust-wallet-token',
    'YGG': 'yield-guild-games',
    'KEEP': 'keep-network',
    'PLA': 'playdapp',
    'MASK': 'mask-network',
    'POND': 'marlin',
    'SFI': 'saffron-finance',
    'MLN': 'melon',
    'OXT': 'orchid-protocol',
    'API3': 'api3',
    'TRB': 'tellor',
    'ERN': 'ethernity-chain',
    'AKRO': 'akropolis',
    'AVA': 'concierge-io',
    'RIF': 'rif-token',
    'SXPOLD': 'swipe',
    'BTTOLD': 'bittorrent-2',
    'ALPHA': 'alpha-finance',
    'LPT': 'livepeer',
    'CVC': 'civic',
    'PERP': 'perpetual-protocol',
    'BOND': 'barnbridge',
    'XNO': 'nano',
    'STPT': 'stp-network',
    'ORN': 'orion-protocol',
    'TRIBE': 'tribe',
    'FIO': 'fio-protocol',
    'IDEX': 'idex',
    'BEPRO': 'bepro-network',
    'ERNOLD': 'ethernity-chain',
    'SUPER': 'superfarm',
    'DODO': 'dodo',
    'XEC': 'ecash',
    'MBL': 'moviebloc',
    'JST': 'just',
    'SUN': 'sun-token',
    'REVV': 'revv',
    'EPS': 'ellipsis',
    'BLZ': 'bluzelle',
    'TKO': 'tokocrypto',
    'WING': 'wing-finance',
    'BRG': 'bridge-oracle',
    'RLY': 'rally',
    'NKN': 'nkn',
    'XVS': 'venus',
    'PHA': 'pha',
    'BADGER': 'badger-dao',
    'FXS': 'frax-share',
    'PHAOLD': 'pha',
    'SOLO': 'solo',
    'DIA': 'dia-data',
    'TVK': 'terra-virtua-kolect',
    'KP3R': 'keep3rv1',
    'VIDT': 'vidt-dao',
    'BURGER': 'burger-swap',
    'CTK': 'certik',
    'DF': 'dforce-token',
    'MIRROR': 'mirror-protocol',
    'AUCTION': 'bounce-token',
    'XDB': 'digitalbits',
    'GTC': 'gitcoin',
    'MOB': 'mobilecoin',
    'LINA': 'linear',
    'RAMP': 'ramp',
    'VR': 'victoria-vr',
    'CKB': 'nervos-network',
    'LIT': 'litentry',
    'BOR': 'boringdao',
    'LAT': 'platon-network',
    'MDT': 'measurable-data-token',
    'FRONT': 'frontier',
    'PROPS': 'props',
    'PRQ': 'parsiq',
    'LTX': 'lattice-token',
    'COTIOLD': 'coti',
    'FEI': 'fei-protocol',
    'POLS': 'polkastarter',
    'BORING': 'boringdao',
    'BETA': 'beta-finance',
    'DUSK': 'dusk-network',
    'HYDRO': 'hydra',
    'TIME': 'chronobank',
    'GODS': 'gods-unchained',
    'JULB': 'justliquidity',
    'LTO': 'lto-network',
    'DEXE': 'dexe',
    'ZKS': 'zkspace',
    'DGD': 'digixdao',
    'SBR': 'saber',
    'EPIC': 'epic-cash',
    'HAPI': 'hapi',
    'STMXOLD': 'stormx',
    'FIDA': 'bonfida',
    'DEGO': 'dego-finance',
    'XDBOLD': 'digitalbits',
    'CVX': 'convex-finance',
    'WOO': 'woo-network',
    'SPS': 'splinterlands',
    'RFOX': 'redfox-labs',
    'ALCX': 'alchemix',
    'ELON': 'dogelon-mars',
    'BUSD': 'binance-usd',
    'USTC': 'terrausd',
    'HT': 'huobi-token',
    'OKB': 'okb',
    'FTM': 'fantom',
    'XMR': 'monero',
    'ZEC': 'zcash',
    'DASH': 'dash',
    'WAVES': 'waves',
    'GUSD': 'gemini-dollar',
    'HBAR': 'hedera',
    'IOTA': 'iota',
    'OMG': 'omisego',
    'PAXG': 'pax-gold',
    'SAFEMOON': 'safemoon',
    'SHIB': 'shiba-inu',
    'WAXP': 'wax',
    'XVG': 'verge',
    'XRP': 'ripple',
    'YFII': 'yfii-finance',
    'ZIL': 'zilliqa'
}

def get_binance_spot_pairs():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)
    data = response.json()
    # Filter to include only pairs that are trading and have USDT as the quote asset
    symbols = [symbol['symbol'] for symbol in data['symbols'] if symbol['status'] == 'TRADING' and symbol['quoteAsset'] == 'USDT']
    return symbols

def get_coingecko_coin_ids():
    cg = CoinGeckoAPI()
    coins_list = cg.get_coins_list()
    return {coin['symbol']: coin['id'] for coin in coins_list}

def update_or_insert_symbol(session, binance_symbol, coingecko_id):
    try:
        # Check if the symbol already exists in the database
        existing_entry = session.query(BinanceCoinGeckoMapping).filter_by(binance_symbol=binance_symbol).first()
        if existing_entry:
            # If exists, update it
            existing_entry.coingecko_id = coingecko_id
        else:
            # If not, insert a new entry
            new_entry = BinanceCoinGeckoMapping(binance_symbol=binance_symbol, coingecko_id=coingecko_id)
            session.add(new_entry)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")

def update_binance_coingecko_mappings():
    binance_pairs = get_binance_spot_pairs()
    coingecko_ids = get_coingecko_coin_ids()

    for pair in binance_pairs:
        base_asset = pair[:-4].upper()

        # Use direct mapping if available
        coingecko_id = direct_mappings.get(base_asset)

        if not coingecko_id:
            # Fallback to dynamic mapping via CoinGecko API
            coingecko_id = coingecko_ids.get(base_asset.lower())

        if coingecko_id:
            update_or_insert_symbol(session, pair, coingecko_id)
        else:
            print(f"Warning: No mapping found for {pair}")

    print("Database update completed.")

if __name__ == "__main__":
    update_binance_coingecko_mappings()
