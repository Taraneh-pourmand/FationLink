from pathlib import Path
from datasets import load_dataset

out_dir = Path(__file__).resolve().parent / "data" / "demand"
out_dir.mkdir(parents=True, exist_ok=True)

ds = load_dataset("snchakri/m5-retail-demand-forecasting-benchmarks", split="test")
ds = ds.select_columns(["item_id", "store_id", "date", "actual"])

ds.to_csv(out_dir / "m5_demand.csv")

print("finished")