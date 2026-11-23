import pytest
from scheduler import sm_2

def test_newcard_success():
	repetition, interval, ef = sm_2(0, 0, 2.5, 4)
	assert repetition == 1
	assert interval == 1
	assert ef == pytest.approx(2.5)

def test_newcard_failure_to_recall():
	repetition, interval, ef = sm_2(0, 0, 2.5, 2)
	assert repetition == 0
	assert interval == 1
	assert ef == pytest.approx(2.18)

def test_rep1_success():
	repetition, interval, ef = sm_2(1, 1, 2.5, 4)
	assert repetition == 2
	assert interval == 6
	assert ef == pytest.approx(2.5)

def test_rep2_success():
	repetition, interval, ef = sm_2(2, 6, 2.5, 4)
	assert repetition == 3
	assert interval == 15
	assert ef == pytest.approx(2.5)

def test_ef_floor():
	repetition, interval, ef = sm_2(2, 6, 1.3, 0)
	assert repetition == 0
	assert interval == 1
	assert ef == pytest.approx(1.3)

def test_mature_card_fail():
	repetition, interval, ef = sm_2(5, 230, 2.5, 0)
	assert repetition == 0
	assert interval == 1
	assert ef == pytest.approx(1.7)

def test_lowest_success():
	repetition, interval, ef = sm_2(2, 6, 2.5, 3)
	assert repetition == 3
	assert interval == 15
	assert ef == pytest.approx(2.36)

def test_highest_success():
	repetition, interval, ef = sm_2(2, 6, 2.5, 5)
	assert repetition == 3
	assert interval == 15
	assert ef == pytest.approx(2.6)

def test_int_behavior():
	repetition, interval, ef = sm_2(3, 15, 2.5, 5)
	assert repetition == 4
	assert interval == 37
	assert ef == pytest.approx(2.6)
