import os
import sys

from dotenv import load_dotenv
from supabase import create_client


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT,
    )


# =========================================================
# ENVIRONMENT
# =========================================================

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


# =========================================================
# APP
# =========================================================

from app import app
from models.file import ProjectFile


# =========================================================
# MIGRATION
# =========================================================

def migrate_media():

    if not SUPABASE_URL:
        print("ERROR: SUPABASE_URL is missing.")
        return

    if not SUPABASE_SECRET_KEY:
        print("ERROR: SUPABASE_SECRET_KEY is missing.")
        return

    if not SUPABASE_BUCKET:
        print("ERROR: SUPABASE_BUCKET is missing.")
        return


    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SECRET_KEY,
    )


    print()
    print("=" * 60)
    print("PLUSH MEDIA MIGRATION")
    print("Local Storage -> Supabase Storage")
    print("=" * 60)
    print()


    with app.app_context():

        files = (
            ProjectFile.query
            .order_by(
                ProjectFile.id.asc()
            )
            .all()
        )


        if not files:
            print("No project files found.")
            return


        print(
            f"Found {len(files)} file(s) to migrate."
        )

        print()


        confirmation = input(
            "Type MIGRATE_MEDIA to continue: "
        ).strip()


        if confirmation != "MIGRATE_MEDIA":

            print()
            print("Migration cancelled.")
            return


        uploaded_count = 0
        failed_count = 0


        for project_file in files:

            # file_url currently looks like:
            # uploads/releases/2/file.pdf

            storage_path = (
                project_file.file_url
                .replace("\\", "/")
                .lstrip("/")
            )


            local_path = os.path.join(
                PROJECT_ROOT,
                "static",
                *storage_path.split("/"),
            )


            print()
            print("-" * 60)
            print(
                f"ID: {project_file.id}"
            )
            print(
                f"File: {project_file.file_name}"
            )
            print(
                f"Local: {local_path}"
            )
            print(
                f"Storage: {storage_path}"
            )


            # ---------------------------------------------
            # CHECK LOCAL FILE
            # ---------------------------------------------

            if not os.path.exists(
                local_path
            ):

                print(
                    "FAILED: Local file does not exist."
                )

                failed_count += 1

                continue


            # ---------------------------------------------
            # READ FILE
            # ---------------------------------------------

            try:

                with open(
                    local_path,
                    "rb",
                ) as file_handle:

                    file_data = (
                        file_handle.read()
                    )


                # -----------------------------------------
                # UPLOAD TO SUPABASE
                # -----------------------------------------

                options = {
                    "upsert": "false",
                }


                if project_file.file_type:

                    options["content-type"] = (
                        project_file.file_type
                    )


                supabase.storage.from_(
                    SUPABASE_BUCKET
                ).upload(
                    path=storage_path,
                    file=file_data,
                    file_options=options,
                )


                print(
                    "SUCCESS: Uploaded."
                )

                uploaded_count += 1


            except Exception as error:

                print(
                    "FAILED:"
                )

                print(
                    error
                )

                failed_count += 1


        print()
        print("=" * 60)
        print("MEDIA MIGRATION FINISHED")
        print("=" * 60)
        print()

        print(
            f"Uploaded: {uploaded_count}"
        )

        print(
            f"Failed:   {failed_count}"
        )

        print(
            f"Total:    {len(files)}"
        )

        print()


if __name__ == "__main__":
    migrate_media()