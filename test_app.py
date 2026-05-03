import pytest
import pandas as pd
from app import fetch_election_dates, generate_voter_checklist

def test_fetch_election_dates():
    """Test that the mocked data returns a valid DataFrame structure."""
    df = fetch_election_dates()
    
    # Assert it returns a DataFrame
    assert isinstance(df, pd.DataFrame)
    
    # Assert expected columns exist
    assert 'title' in df.columns
    assert 'date' in df.columns
    assert 'description' in df.columns
    
    # Assert data is populated
    assert not df.empty

def test_generate_voter_checklist_default():
    """Test standard checklist without special conditions."""
    checklist = generate_voter_checklist(first_time="No", vote_method="In-person")
    assert len(checklist) == 3
    assert "Verify your voter registration status online." in checklist
    assert "Check the polling hours and plan what time you will vote." in checklist

def test_generate_voter_checklist_first_time():
    """Test checklist for first-time voters."""
    checklist = generate_voter_checklist(first_time="Yes", vote_method="In-person")
    assert len(checklist) == 5
    # Check for specific first-time text
    assert any("valid form of photo ID" in item for item in checklist)

def test_generate_voter_checklist_absentee():
    """Test checklist for absentee voters."""
    checklist = generate_voter_checklist(first_time="No", vote_method="Absentee")
    assert len(checklist) == 5
    assert any("absentee/mail-in ballot before the deadline" in item for item in checklist)

def test_generate_voter_checklist_all_conditions():
    """Test checklist when all conditions are true."""
    checklist = generate_voter_checklist(first_time="Yes", vote_method="Mail-in")
    assert len(checklist) == 7 
    assert any("absentee/mail-in ballot before the deadline" in item for item in checklist)
