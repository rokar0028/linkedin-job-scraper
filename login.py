"""
Root entrypoint for LinkedIn session login.
Delegates to scripts.login.
"""
from scripts.login import login_and_save_session

if __name__ == "__main__":
    login_and_save_session()
