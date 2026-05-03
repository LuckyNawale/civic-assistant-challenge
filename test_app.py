import pytest
import pandas as pd
from app import fetch_election_dates, generate_voter_checklist

def test_fetch_election_dates():
    """Test that the mocked (or real) data returns a valid DataFrame structure."""
    df = fetch_election_dates()
    
    # Assert it returns a DataFrame
    assert isinstance(df, pd.DataFrame)
    
    # Assert expected columns exist
    assert 'title' in df.columns
    assert 'date' in df.columns
    assert 'description' in df.columns
    
    # Assert data is populated
    assert not df.empty
    
    # Assert dates are actually datetime objects
    assert pd.api.types.is_datetime64_any_dtype(df['date'])

def test_generate_voter_checklist_default():
    """Test standard checklist without special conditions."""
    checklist = generate_voter_checklist(is_first_time=False, is_absentee=False, needs_accommodation=False)
    assert len(checklist) == 2
    assert "Verify your voter registration status online." in checklist

def test_generate_voter_checklist_first_time():
    """Test checklist for first-time voters."""
    checklist = generate_voter_checklist(is_first_time=True, is_absentee=False, needs_accommodation=False)
    assert len(checklist) == 4
    # Check for specific first-time text
    assert any("valid form of ID" in item for item in checklist)

def test_generate_voter_checklist_absentee():
    """Test checklist for absentee voters."""
    checklist = generate_voter_checklist(is_first_time=False, is_absentee=True, needs_accommodation=False)
    assert len(checklist) == 5
    assert any("absentee ballot before the deadline" in item for item in checklist)

def test_generate_voter_checklist_all_conditions():
    """Test checklist when all conditions are true."""
    checklist = generate_voter_checklist(is_first_time=True, is_absentee=True, needs_accommodation=True)
    assert len(checklist) == 8  # 2 base + 2 first-time + 3 absentee + 1 accommodation
    assert any("accessible voting options" in item for item in checklist)
