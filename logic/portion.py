def portion_to_gram(food_name: str, unit: str, takaran_df):
    if takaran_df is None or takaran_df.empty:
        raise ValueError("Data takaran kosong atau tidak tersedia")

    food_name = food_name.strip().lower()
    unit = unit.strip().lower()

    df = takaran_df.copy()

    df["food_name"] = (
        df["food_name"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["unit"] = (
        df["unit"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    row = df[
        (df["food_name"] == food_name) &
        (df["unit"] == unit)
    ]

    if row.empty:
        raise ValueError(f"Takaran tidak ditemukan: {food_name} ({unit})")

    gram = row.iloc[0]["gram"]

    try:
        return float(gram)
    except (TypeError, ValueError):
        raise ValueError(f"Nilai gram tidak valid untuk {food_name} ({unit})")
