import pandas as pd
from sqlalchemy import create_engine

def batch_load_sql(query: str) -> pd.DataFrame:
    CHUNKSIZE = 200000
    engine = create_engine(
        "postgresql://robot-startml-ro:pheiph0hahj1Vaif@"
        "postgres.lab.karpov.courses:6432/startml"
    )
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
        chunks.append(chunk_dataframe)
    conn.close()
    return pd.concat(chunks, ignore_index=True)

def load_features(version) -> pd.DataFrame:
    query = f'SELECT * FROM {version}'
    user_features = batch_load_sql(query)
    return user_features

if __name__ == "__main__":
    user_features = load_features()