"""Deterministic backfill runner for Nova-Seeds indexer."""

import argparse
from .indexer import run_once


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--from-block', type=int, default=None)
    parser.add_argument('--to-block', type=int, default=None)
    args = parser.parse_args()

    result = run_once(start_override=args.from_block, end_override=args.to_block)
    print(result)


if __name__ == '__main__':
    main()
