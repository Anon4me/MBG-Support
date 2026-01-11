<<<<<<< HEAD
def portion_to_gram(food_name: str, unit: str, takaran_df):
    row = takaran_df[
        (takaran_df["food_name"].str.strip().str.lower() == food_name.strip().lower()) &
        (takaran_df["unit"].str.strip().str.lower() == unit.strip().lower())
    ]

    if row.empty:
        raise ValueError(f"Takaran tidak ditemukan: {food_name} ({unit})")

    return float(row.iloc[0]["gram"])
=======
def portion_to_gram(food_name: str, unit: str, takaran_df):
    row = takaran_df[
        (takaran_df["food_name"].str.strip().str.lower() == food_name.strip().lower()) &
        (takaran_df["unit"].str.strip().str.lower() == unit.strip().lower())
    ]

    if row.empty:
        raise ValueError(f"Takaran tidak ditemukan: {food_name} ({unit})")

    return float(row.iloc[0]["gram"])
>>>>>>> 2973111988d9054ce4d217ed6dc3b0b73b6372ba
