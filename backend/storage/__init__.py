from .base import SubmissionStorage


def get_storage_backend(config) -> SubmissionStorage:
    backend = config["STORAGE_BACKEND"]

    # Imports are inside each branch so you only need the libraries for the
    # backend you actually use.
    if backend == "none":
        from .null_storage import NullStorage
        return NullStorage()

    if backend == "google_sheets":
        from .google_sheets_storage import GoogleSheetsStorage
        return GoogleSheetsStorage(
            service_account_file=config["GOOGLE_SERVICE_ACCOUNT_FILE"],
            sheet_id=config["GOOGLE_SHEET_ID"],
            worksheet_name=config["GOOGLE_SHEET_WORKSHEET"],
        )

    if backend == "mysql":
        from .mysql_storage import MySQLStorage
        return MySQLStorage(
            host=config["MYSQL_HOST"],
            port=config["MYSQL_PORT"],
            user=config["MYSQL_USER"],
            password=config["MYSQL_PASSWORD"],
            database=config["MYSQL_DATABASE"],
        )

    raise ValueError(
        f"Unknown STORAGE_BACKEND '{backend}'. Use 'none', 'mysql' or 'google_sheets'."
    )
