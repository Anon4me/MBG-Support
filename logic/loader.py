<<<<<<< HEAD
import pandas as pd
from loguru import logger


def load_csv(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)

        if df.empty:
            raise ValueError("CSV file is empty")

        df.columns = df.columns.str.strip()

        logger.info(f"Loaded CSV: {path} ({len(df)} rows)")
        return df

    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise

    except Exception as e:
        logger.exception(f"Failed loading CSV: {path}")
        raise RuntimeError(e)
=======
import pandas as pd
from loguru import logger


def load_csv(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)

        if df.empty:
            raise ValueError("CSV file is empty")

        df.columns = df.columns.str.strip()

        logger.info(f"Loaded CSV: {path} ({len(df)} rows)")
        return df

    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise

    except Exception as e:
        logger.exception(f"Failed loading CSV: {path}")
        raise RuntimeError(e)
>>>>>>> 2973111988d9054ce4d217ed6dc3b0b73b6372ba
