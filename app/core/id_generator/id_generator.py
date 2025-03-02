# id_generator.py
from enum import IntEnum
import nanoid
import typing


class EntityType(IntEnum):
    ACCOUNT = 0
    USER = 1
    HUBSPOT = 2
    PLAN = 3
    WORKSPACE = 4
    DOCUMENT = 5
    DOCUMENT_CHUNK = 6
    DOCUMENT_EMBEDDING = 7
    EMBEDDING_SEARCH = 8


class IDGenerator:
    ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
    ID_LENGTH = 21

    PREFIX_MAP = {
        EntityType.ACCOUNT: "acc",
        EntityType.USER: "usr",
        EntityType.HUBSPOT: "hb",
        EntityType.PLAN: "pln",
        EntityType.WORKSPACE: "wks",
        EntityType.DOCUMENT: "doc",
        EntityType.DOCUMENT_CHUNK: "chk",
        EntityType.DOCUMENT_EMBEDDING: "emb",
        EntityType.EMBEDDING_SEARCH: "srch",
    }

    @classmethod
    def generate_id(cls, entity_type: EntityType) -> str:
        """
        Generate a unique ID for the given entity type.

        Args:
            entity_type (EntityType): The type of entity to generate an ID for

        Returns:
            str: A unique ID with the appropriate prefix

        Raises:
            ValueError: If an unknown entity type is provided
        """
        if entity_type not in cls.PREFIX_MAP:
            raise ValueError(f"Unknown entity type: {entity_type}")

        random_id = nanoid.generate(alphabet=cls.ALPHABET, size=cls.ID_LENGTH)

        prefix = cls.PREFIX_MAP[entity_type]

        return f"{prefix}_{random_id}"


def generate_account_id() -> str:
    """Generate a unique ID for an account."""
    return IDGenerator.generate_id(EntityType.ACCOUNT)


def generate_user_id() -> str:
    """Generate a unique ID for a user."""
    return IDGenerator.generate_id(EntityType.USER)


def generate_hubspot_id() -> str:
    """Generate a unique ID for OAuth credentials."""
    return IDGenerator.generate_id(EntityType.HUBSPOT)


def generate_plan_id() -> str:
    """Generate a unique ID for a plans."""
    return IDGenerator.generate_id(EntityType.PLAN)


def generate_workspace_id() -> str:
    """Generate a unique ID for a workspace."""
    return IDGenerator.generate_id(EntityType.WORKSPACE)


def generate_document_id() -> str:
    """Generate a unique ID for a document."""
    return IDGenerator.generate_id(EntityType.DOCUMENT)


def generate_document_chunk_id() -> str:
    """Generate a unique ID for a document chunk."""
    return IDGenerator.generate_id(EntityType.DOCUMENT_CHUNK)


def generate_document_embedding_id() -> str:
    """Generate a unique ID for a document embedding."""
    return IDGenerator.generate_id(EntityType.DOCUMENT_EMBEDDING)


def generate_embedding_search_id() -> str:
    """Generate a unique ID for an embedding search record."""
    return IDGenerator.generate_id(EntityType.EMBEDDING_SEARCH)


def get_id_generator(entity_type: EntityType) -> typing.Callable[[], str]:
    """
    Get a function that generates IDs for a specific entity type.

    Args:
        entity_type (EntityType): The type of entity to generate IDs for

    Returns:
        Callable[[], str]: A function that generates IDs for the specified entity type
    """
    return lambda: IDGenerator.generate_id(entity_type)


if __name__ == "__main__":
    print("Account ID:", generate_account_id())
    print("User ID:", generate_user_id())
    print("OAuth ID:", generate_hubspot_id())
    print("Plan ID:", generate_plan_id())
    print("Workspace ID:", generate_workspace_id())
    print("Document ID:", generate_document_id())
    print("Document Chunk ID:", generate_document_chunk_id())
    print("Document Embedding ID:", generate_document_embedding_id())
    print("Embedding Search ID:", generate_embedding_search_id())