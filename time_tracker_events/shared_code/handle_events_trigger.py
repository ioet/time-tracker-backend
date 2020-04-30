import logging
import uuid
from datetime import datetime

import azure.functions as func


def main(documents: func.DocumentList, events: func.Out[func.Document]):
    if documents:
        new_events = func.DocumentList()

        for doc in documents:
            logging.info(doc.to_json())

            event_context = doc.get("_last_event_ctx")
            if event_context is not None:
                new_events.append(func.Document.from_dict({
                    "id": str(uuid.uuid4()),
                    "date": datetime.utcnow().isoformat(),
                    "user_id": event_context.get("user_id"),
                    "action": event_context.get("action"),
                    "description": event_context.get("description"),
                    "item_id": doc.get("id"),
                    "container_id": event_context.get("container_id"),
                    "session_id": event_context.get("session_id"),
                    "tenant_id": event_context.get("tenant_id"),
                }))
            else:
                logging.warning("- Not saved!")

        if len(new_events):
            events.set(new_events)
        else:
            logging.warning("No valid events were found!")
