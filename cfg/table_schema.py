from enum import StrEnum


class Cols(StrEnum):
    """class to store the column names in the data tabble"""

    ID = "id"
    NAME = "name"
    BIRTHDAY = "birthday"
    DEATHDATE = "deathdate"
    SPOUSE = "spouse"
    PARENT = "parent"
    BIRTHPLACE = "birthplace"
    MARRIAGEDATE = "marriagedate"
