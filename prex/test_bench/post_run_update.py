import os
import argparse

def get_usage():
    return """
    Usage:
         post_run_update.py <run_number> -c <db_connection_string> --update --reason=[start, end, repair]
    """

def update():

    description = "Script for PVDB udpates after CODA run end"
    parser = argparse.ArgumentParser(description=description, usage=get_usage())
    parser.add_argument("--run", type=str, help="Run number")
    args = parser.parse_args()

if __name__ == "__main__":
    update()
