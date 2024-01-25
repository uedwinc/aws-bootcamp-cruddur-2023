from datetime import datetime, timedelta, timezone
from opentelemetry import trace
import logging

from lib.db import pool, query_wrap_object, query_wrap_array

tracer = trace.get_tracer("home.activities")

class HomeActivities:
  def run(logger):
    logger.info("HomeActivities")
    with tracer.start_as_current_span("home-activities-trace-data"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())
      span.set_attribute("app.result_length", len(results))

      sql = query_wrap_array("""
      SELECT * FROM activities
      """)
      print(sql)
      print("SQL--------------")
      with pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(sql)
          # this will return a tuple
          # the first field being the data
          json = cur.fetchone()
      print("==================")
      return json[0]