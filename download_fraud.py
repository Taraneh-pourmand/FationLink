from pathlib import Path
from datasets import load_dataset

out_dir = Path(__file__).resolve().parent / "data" / "fraud"
out_dir.mkdir(parents=True, exist_ok=True)

ds = load_dataset("David-Egea/Creditcard-fraud-detection", split="train")
ds.to_csv(out_dir / "creditcard.csv")

print("finished")