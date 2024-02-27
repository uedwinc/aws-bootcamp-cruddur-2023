from datetime import datetime, timedelta, timezone
from opentelemetry import trace
import logging

from lib.db import db

#tracer = trace.get_tracer("home.activities")

class HomeActivities:
  #def run(logger):
    #logger.info("HomeActivities")
    #with tracer.start_as_current_span("home-activities-trace-data"):
    #  span = trace.get_current_span()
    #  now = datetime.now(timezone.utc).astimezone()
    #  span.set_attribute("app.now", now.isoformat())
    #  span.set_attribute("app.result_length", len(results))

  def run(cognito_user_id=None):
    sql = db.template('activities','home')
    results = db.query_array_json(sql)
    return results
