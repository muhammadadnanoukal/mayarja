from enum import Enum


class UserInsuranceState(Enum):
    NO_REQUEST = 1
    BOTH_WAITING = 2
    ONE_WAITING = 3
    EXCEPTION = 4
    REQUEST_TYPE_1 = 5
    REQUEST_TYPE_2 = 6
    PAYMENT_REQUIRED = 7
    CANT_MAKE_REQUEST = 8
    ACCESS_DENIED = 9
    PAID = 10
    BOTH_PAYMENT_REQUIRED = 11