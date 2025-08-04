from dataclasses import dataclass


@dataclass
class TransactionDeps:
    conversation_id: str
    transaction_id: str
