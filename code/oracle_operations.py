def filter_oracle(df_clones):
    return df_clones[
        (df_clones["classification"] == "QS")
        | (df_clones["classification"] == "EX")
        | (df_clones["classification"] == "UD")
    ]
