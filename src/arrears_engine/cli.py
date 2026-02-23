from __future__ import annotations


import argparse
from datetime import date, datetime
from html import parser


from arrears_engine.io import load_ledger, load_tenants

from .config import load_config
from .app import run_pipeline

def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError("Date must be YYYY-MM-DD")
    

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="arrears-engine",
        description="Tenant Arrears Tracker + Reminder Engine",
    )

    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run arrears pipeline")
    run_parser.add_argument(
        "--config",
        required=True,
        help="Path to config JSON file",
    )
    run_parser.add_argument(
        "--as-of",
        type=parse_date,
        default=date.today(),
        help="As-of date (YYYY-MM-DD)",
    )
    run_parser.add_argument(
        "--out-dir",
        default="outputs",
        help="Output directory",
    )
    
    validate_parser = subparsers.add_parser("validate",
                                             help="Validate config and input workbook")
    validate_parser.add_argument(
        "--config",
        required=True,
        help="Path to config JSON file",
    )

    status_parser = subparsers.add_parser("status", help="Show current arrears status")
    status_parser.add_argument("--config",
            required=True, 
            help="Path to config JSON file")
    
    args = parser.parse_args()

    if args.command == "run":
        cfg = load_config(args.config)
        paths = run_pipeline(cfg, as_of=args.as_of, out_dir=args.out_dir)

        print("Pipeline completed.")
        for k, v in paths.items():
            print(f"{k}: {v}")

    elif args.command == "validate":
        cfg = load_config(args.config)

    # Try loading inputs only
        load_tenants(cfg.workbook_path, cfg.tenants_sheet)
        load_ledger(cfg.workbook_path, cfg.ledger_sheet)

        print("Validation successful. Inputs are valid.")
    elif args.command == "status":
        cfg = load_config(args.config)

        print("Config status")
        print(f"workbook_path: {cfg.workbook_path}")
        print(f"tenants_sheet: {cfg.tenants_sheet}")
        print(f"ledger_sheet: {cfg.ledger_sheet}")
        print(f"reminder_rules count: {len(cfg.reminder_rules)}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()