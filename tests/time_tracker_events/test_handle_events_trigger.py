import azure.functions as func
from faker import Faker

from time_tracker_events.handle_events_trigger import main as main_handler

fake = Faker()


class OutImpl(func.Out):
    def __init__(self):
        self.val = None

    def set(self, val: func.DocumentList) -> None:
        self.val = val

    def get(self) -> func.DocumentList:
        return self.val


def generate_sample_document(has_event_ctx=True):
    result = {
        "id": fake.uuid4(),
        "tenant_id": fake.uuid4(),
    }

    if has_event_ctx:
        result["_last_event_ctx"] = {
            "user_id": fake.name(),
            "action": "update",
            "description": fake.paragraph(),
            "container_id": fake.uuid4(),
            "session_id": fake.uuid4(),
            "tenant_id": result["tenant_id"],
        }

    return result


def test_main_handler_should_generate_events_if_hidden_attrib_is_found():
    out = OutImpl()
    documents = func.DocumentList()
    for i in range(10):
        documents.append(func.Document.from_dict(generate_sample_document()))
    for i in range(5):
        documents.append(func.Document.from_dict(generate_sample_document(False)))

    main_handler(documents, out)

    assert len(out.get()) == 10
