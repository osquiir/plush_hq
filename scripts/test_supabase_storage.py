import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()


SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)

SUPABASE_SECRET_KEY = os.getenv(
    "SUPABASE_SECRET_KEY"
)

SUPABASE_BUCKET = os.getenv(
    "SUPABASE_BUCKET"
)


def test_storage():

    if not SUPABASE_URL:
        print("Missing SUPABASE_URL")
        return

    if not SUPABASE_SECRET_KEY:
        print("Missing SUPABASE_SECRET_KEY")
        return

    if not SUPABASE_BUCKET:
        print("Missing SUPABASE_BUCKET")
        return


    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SECRET_KEY,
    )


    try:

        files = (
            supabase
            .storage
            .from_(SUPABASE_BUCKET)
            .list()
        )

        print()
        print("Storage connection successful!")
        print()
        print(f"Bucket: {SUPABASE_BUCKET}")
        print()
        print("Files:")
        print(files)

    except Exception as error:

        print()
        print("Storage connection failed.")
        print()
        print(error)


if __name__ == "__main__":
    test_storage()