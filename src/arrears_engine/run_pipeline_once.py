from datetime import date
from arrears_engine.config import load_config
from arrears_engine.app import run_pipeline

cfg = load_config("data/config.example.json")
paths = run_pipeline(cfg, as_of=date.today(), out_dir="outputs")
print(paths)