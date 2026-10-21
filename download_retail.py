from pathlib import Path
from datasets import load_dataset

out_dir = Path(__file__).resolve().parent / "data" / "demand"
out_dir.mkdir(parents=True, exist_ok=True)

ds = load_dataset("attik/Online-Retail-II-UCI", split="train")
ds.to_csv(out_dir / "online_retail_II.csv")

print("finished") 