from random import randrange
import re


def parse_roll(rollstring):
    rollstring = rollstring.lower()
    dice_regex = re.compile(r'(?P<dice_number>\d*)?d(?P<dice_value>\d*)(?P<flat_bonus>[\+-]\d+)?')
    parsed_rollstring = dice_regex.search(rollstring)

    dice_number = parsed_rollstring.group('dice_number') or 1
    flat_bonus = parsed_rollstring.group('flat_bonus') or 0
    return int(dice_number), int(parsed_rollstring.group('dice_value')), int(flat_bonus)


class Roll:
    def __init__(self, dice_number=1, dice_value=0, flat_bonus=0):
        self.rolls = []
        self.dice_number = dice_number
        self.dice_value = dice_value
        self.flat_bonus = flat_bonus
        self._result = None

    @classmethod
    def from_rollstring(cls, rollstring):
        return cls(*parse_roll(rollstring))

    @property
    def result(self):
        if self._result:
            return self._result
        else:
            print("calculating")
            return self.calculate()

    def calculate(self):
        self.rolls = [randrange(1, self.dice_value + 1) for _ in range(self.dice_number)]
        self._result = sum(self.rolls) + self.flat_bonus
        return self._result

    def as_detailed(self):
        self.result  # ensure roll is rolled
        rolls = ' + '.join(f'({roll})' for roll in self.rolls)
        return f"{rolls} {self.flat_bonus_to_string()}"

    def flat_bonus_to_string(self):
        if self.flat_bonus:
            if self.flat_bonus > 0:
                return '+ ' + str(self.flat_bonus)
            else:
                return str(self.flat_bonus)[0] + ' ' + str(self.flat_bonus)[1:]
        return ''
