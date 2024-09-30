import enum


class TransactionType(enum.Enum):
    ton_in = 'ton in'
    ton_out = 'ton out'
    jetton_in = 'jetton in'
    jetton_out = 'jetton out'
