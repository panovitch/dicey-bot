from rolling import Roll, parse_roll
from db import DB
from unittest import mock, TestCase
import os
import pytest

@mock.patch('rolling.randrange')
def test_roll_one_dice(randrange):
    randrange.return_value = 20
    r = Roll.from_rollstring('1d20')
    assert r.result == 20
    randrange.assert_called_once_with(1, 20)


@mock.patch('rolling.randrange')
def test_roll_another_dice(randrange):
    randrange.return_value = 6
    r = Roll.from_rollstring('1d6')
    assert r.result == 6
    randrange.assert_called_once_with(1, 6)

@mock.patch('rolling.randrange')
def test_roll_multiple_die(randrange):
    randrange.return_value = 20
    r = Roll.from_rollstring('3d20')
    assert r.result == 60
    randrange.assert_has_calls([
        mock.call(1, 20),
        mock.call(1, 20),
        mock.call(1, 20)
    ])

@mock.patch('rolling.randrange')
def test_die_with_plus(randrange):
    randrange.return_value = 6
    r = Roll.from_rollstring('2d6+5')
    assert r.result == 17
    randrange.assert_has_calls([
        mock.call(1, 6),
        mock.call(1, 6),
    ])

@mock.patch('rolling.randrange')
def test_die_with_minus(randrange):
    randrange.return_value = 1
    r = Roll.from_rollstring('2d6-5')
    assert r.result == -3
    randrange.assert_has_calls([
        mock.call(1, 6),
        mock.call(1, 6),
    ])


def test_parse_dice_string():
    assert (2, 6, 5) == parse_roll('2d6+5')

def test_parse_dice_string_neg():
    assert (2, 20, -5) == parse_roll('2d20-5')

def test_parse_default_amount():
    assert (1, 20, -5) == parse_roll('d20-5')

@mock.patch('rolling.randrange')
def test_as_detailed(randrange):
    randrange.return_value = 6
    r = Roll.from_rollstring('2d6-5')
    assert r.as_detailed() == '(6) + (6) - 5'

@mock.patch('rolling.randrange')
def test_as_detailed_plus(randrange):
    randrange.return_value = 6
    r = Roll.from_rollstring('2d6+5')
    assert r.as_detailed() == '(6) + (6) + 5'


@pytest.fixture
def teardown_db():
    yield 'test.db'
    os.remove('test.db')

def test_db_save_user(db_name):
    user_info = {
        'key': 'value'
    }
    user_id = 'test'
    db = DB(db_name, user_id)
    db.save(user_info)

    assert db.load()['key'] == 'value'


def test_db_get_previous_roll(db_name):
    db = DB(db_name, 'test_id')

    db.save_previous_roll('test_roll')
    prev_roll = db.get_previous_roll()
    assert prev_roll == 'test_roll'


def test_db_save_roll(db_name):
    user_id = 'test'
    db = DB(db_name, user_id)
    db.save_roll('attack', 'testroll')

    assert db.get_saved_roll('attack') == 'testroll'