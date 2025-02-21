# id_generator.py
from enum import IntEnum
import nanoid
import typing


class EntityType(IntEnum):
    ACCOUNT = 0
    USER = 1
    OAUTH_CREDENTIALS = 2
    PLAN = 3


class IDGenerator:
    # Using same alphabet as the Go version
    ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
    ID_LENGTH = 21  # Same length as Go version

    # Prefix mapping for each entity type
    PREFIX_MAP = {
        EntityType.ACCOUNT: "acc",
        EntityType.USER: "usr",
        EntityType.OAUTH_CREDENTIALS: "oauth",
        EntityType.PLAN: "pln"
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

        # Generate the random part of the ID
        random_id = nanoid.generate(alphabet=cls.ALPHABET, size=cls.ID_LENGTH)

        # Get the prefix for this entity type
        prefix = cls.PREFIX_MAP[entity_type]

        # Return the prefixed ID
        return f"{prefix}_{random_id}"


# Example usage functions
def generate_account_id() -> str:
    """Generate a unique ID for an account."""
    return IDGenerator.generate_id(EntityType.ACCOUNT)


def generate_user_id() -> str:
    """Generate a unique ID for a user."""
    return IDGenerator.generate_id(EntityType.USER)


def generate_oauth_id() -> str:
    """Generate a unique ID for OAuth credentials."""
    return IDGenerator.generate_id(EntityType.OAUTH_CREDENTIALS)


def generate_plan_id() -> str:
    """Generate a unique ID for a plans."""
    return IDGenerator.generate_id(EntityType.PLAN)


# Convenience function to get ID generator for a specific entity type
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
    # Example usage
    print("Account ID:", generate_account_id())  # e.g. acc_7h3j4k5l6m7n8p9q0r1s
    print("User ID:", generate_user_id())  # e.g. usr_1a2b3c4d5e6f7g8h9i0j
    print("OAuth ID:", generate_oauth_id())  # e.g. oauth_9w8v7u6t5s4r3q2p1o0
    print("Plan ID:", generate_plan_id())  # e.g. pln_2x3y4z5a6b7c8d9e0f1
