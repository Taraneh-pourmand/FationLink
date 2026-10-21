from pathlib import Path
from datasets import load_dataset

out_dir = Path(__file__).resolve().parent / "data" / "reviews"
out_dir.mkdir(parents=True, exist_ok=True)

ds = load_dataset("Yelp/yelp_review_full")

ds["train"].to_csv(out_dir / "yelp_train.csv")
ds["test"].to_csv(out_dir / "yelp_test.csv")

print("finished")