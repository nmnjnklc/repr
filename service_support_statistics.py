from mysql.connector.errors import (
    InterfaceError, DatabaseError, OperationalError
)

import requests
import os

from datetime import datetime, timedelta
from pytz import timezone
from dotenv import dotenv_values
from pathlib import Path
from json import dumps

from utils.mail_sender import MailSender
from utils.data_fetcher import fetch_data

from properties.service_support_statistics import properties


def get_timestamps() -> tuple[datetime.date, datetime.date, int, int]:
    end: datetime = datetime.now(
        tz=timezone('Europe/Belgrade')
    ).replace(hour=6, minute=0, second=0, microsecond=0)

    start: datetime = end - timedelta(days=7)

    return start.date() \
         , end.date() \
         , int(round(start.timestamp())) * 1000 \
         , int(round(end.timestamp())) * 1000


def main() -> None:
    base: Path = Path(__file__).resolve().parent
    env: dict = dotenv_values(
        dotenv_path=Path(base, ".env")
    )

    apps: dict = properties.get("apps")
    email_to: list[str] = properties.get("email_to")

    ms: MailSender = MailSender(
        mail_username=env.get("MAIL_USERNAME"),
        mail_password=env.get("MAIL_PASSWORD"),
    )

    start_date, end_date, start_timestamp, end_timestamp = get_timestamps()

    files: list[Path] = []
    for app, data in apps.items():
        params = data.get("connection")
        accounts = data.get("accounts")

        for account in accounts:
            file: Path = Path(base, f"{app}_{account}.csv")
            if file.exists():
                os.remove(path=Path(base, f"{app}_{account}.csv"))

            query = f"""
                SELECT b.readableEntryDate
                     , b.shift
                     , CONCAT(
                           ROUND(AVG(b.duration) / 60, 1)
                         , " mins"
                       ) AS avgDuration
                FROM (
                    SELECT a.*
                         , ROUND(
                               PERCENT_RANK() OVER(PARTITION BY a.readableEntryDate ORDER BY a.readableEntryDate ASC, a.duration ASC) * 100
                             , 2
                           ) AS percent
                    FROM (
                        SELECT FROM_UNIXTIME(ah.entryDate / 1000, "%M %d") AS readableEntryDate
                             , ROUND((ah.finishDate - ah.entryDate) / 1000, 2) AS duration
                             , ah.entryDate
                             , ah.finishDate
                             , ah.shift
                             , c.aMonitoringAllowed
                        FROM actions_history ah
                        JOIN companies c
                            ON c.id = ah.company_id
                        WHERE c.aMonitoringAllowed = {0 if account == "companies" else 1}
                        AND ah.entryDate BETWEEN {start_timestamp} AND {end_timestamp}
                        ORDER BY readableEntryDate ASC, duration ASC
                    ) AS a
                ) AS b
                WHERE b.percent BETWEEN 20 AND 80
                GROUP BY b.readableEntryDate, b.shift
                ORDER BY b.readableEntryDate, b.shift;
            """

            try:
                result: list[dict] = fetch_data(query=query, params=params, as_dict=True)
                header: list[str] = [str(key) for key in result[0].keys()]

                with open(file=file, mode="w") as f:
                    f.write(", ".join(header))
                    f.write("\n")
                    for row in result:
                        values = [str(value) for value in row.values()]
                        f.write(", ".join(values))
                        f.write("\n")

                files.append(file)

            except (InterfaceError, DatabaseError, OperationalError, IndexError) as e:
                requests.post(
                    url=env.get("WEBHOOK_URL"),
                    data=dumps(dict(
                        username="Slack Reporter",
                        text=f"service-support-statistics - {app} - {e.orig.args[1]}"
                )))
                continue

    ms.send_email_with_attachments(
        files=files,
        to=email_to,
        subject=f"Service Support Statistics for period {start_date} - {end_date}",
        sender="DEV Checker"
    )

if __name__ == "__main__":
    if datetime.today().weekday() == 0:  # Checking if today is Monday.
        main()                           # Monday, as the first day of the week, will be 0.
