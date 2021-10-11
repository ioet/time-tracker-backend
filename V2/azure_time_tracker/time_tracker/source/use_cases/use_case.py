def get_all():
    activity = [
        {
            "name": "Development",
            "description": "Development",
            "tenant_id": "cc925a5d-9644-4a4f-8d99-0bee49aadd05",
            "id": "c61a4a49-3364-49a3-a7f7-0c5f2d15072b",
            "deleted": "b4327ba6-9f96-49ee-a9ac-3c1edf525172",
            "status": "active",
        },
        {
            "name": "Management",
            "description": "description test",
            "tenant_id": "cc925a5d-9644-4a4f-8d99-0bee49aadd05",
            "id": "94ec92e2-a500-4700-a9f6-e41eb7b5507c",
            "deleted": "7cf6efe5-a221-4fe4-b94f-8945127a489a",
            "status": "active",
        },
    ]

    return activity


def get_by_id(id):

    return {
        "name": "Management",
        "description": "description test",
        "tenant_id": "cc925a5d-9644-4a4f-8d99-0bee49aadd05",
        "id": "94ec92e2-a500-4700-a9f6-e41eb7b5507c",
        "deleted": "7cf6efe5-a221-4fe4-b94f-8945127a489a",
        "status": "active",
    }
