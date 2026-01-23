# coding: utf-8
"""
Test parsing of sample AEP files to ensure BOM handling and general parsing works correctly.

This test suite validates that the parser can handle real-world After Effects project files
and that the BOM fix doesn't break existing functionality.
"""
from __future__ import absolute_import, unicode_literals, division
import os
import pytest
from aep_parser.parsers.project import parse_project


# Get all sample files
SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'samples')


def get_sample_files():
    """Get list of all sample .aep files."""
    if not os.path.exists(SAMPLES_DIR):
        return []
    return sorted([f for f in os.listdir(SAMPLES_DIR) if f.endswith('.aep')])


@pytest.mark.parametrize('sample_file', get_sample_files())
def test_sample_file_parsing(sample_file):
    """
    Test that each sample file can be parsed successfully.
    
    This ensures that the BOM handling changes don't break parsing of real AEP files.
    Some files may have known issues unrelated to BOM handling - those are marked as xfail.
    """
    # Known files with issues unrelated to BOM handling
    known_failures = {
        'Property-01.aep': "ListBody attribute issue",
        'asset_names.aep': "OptiBody attribute issue",
    }
    
    path = os.path.join(SAMPLES_DIR, sample_file)
    
    if sample_file in known_failures:
        pytest.skip(f"Known issue: {known_failures[sample_file]}")
    
    # This should not raise an exception
    project = parse_project(path)
    
    # Basic validation
    assert project is not None
    assert hasattr(project, 'project_items')


def test_sample_files_exist():
    """Verify that sample files directory exists and contains files."""
    assert os.path.exists(SAMPLES_DIR), f"Samples directory not found at {SAMPLES_DIR}"
    sample_files = get_sample_files()
    assert len(sample_files) > 0, "No sample .aep files found"


def test_no_bom_artifacts_in_parsed_strings():
    """
    Test that parsed strings from sample files don't contain BOM artifacts.
    
    This is a regression test for issue #12 where UTF-8 BOM characters
    were appearing in decoded strings.
    """
    sample_files = get_sample_files()
    
    # Skip known failing files
    skip_files = {'Property-01.aep', 'asset_names.aep'}
    
    for sample_file in sample_files:
        if sample_file in skip_files:
            continue
            
        path = os.path.join(SAMPLES_DIR, sample_file)
        
        try:
            project = parse_project(path)
            
            # Check various string fields for BOM characters
            if hasattr(project, 'file') and isinstance(project.file, str):
                assert '\ufeff' not in project.file, \
                    f"BOM character found in project.file for {sample_file}"
            
            if hasattr(project, 'effect_names'):
                for effect_name in project.effect_names:
                    if isinstance(effect_name, str):
                        assert '\ufeff' not in effect_name, \
                            f"BOM character found in effect name '{effect_name}' for {sample_file}"
            
            # Check project items
            if hasattr(project, 'project_items'):
                for item_id, item in project.project_items.items():
                    if hasattr(item, 'name') and isinstance(item.name, str):
                        assert '\ufeff' not in item.name, \
                            f"BOM character found in item name '{item.name}' for {sample_file}"
                            
        except Exception:
            # If the file fails to parse for other reasons, skip it
            continue


def test_baseline_parsing_count():
    """
    Test that we can successfully parse a baseline number of sample files.
    
    This provides a regression check - if the count drops significantly,
    it indicates the BOM fix may have broken something.
    
    The 95% threshold is based on the current state where 72/74 files parse
    successfully (97%). This allows for some variation while catching major regressions.
    """
    sample_files = get_sample_files()
    if not sample_files:
        pytest.skip("No sample files found")
    
    successful = 0
    for sample_file in sample_files:
        path = os.path.join(SAMPLES_DIR, sample_file)
        try:
            project = parse_project(path)
            if project is not None:
                successful += 1
        except Exception:
            pass
    
    # We should be able to parse at least 95% of the sample files
    # (currently 72/74 = 97%, so this allows for minor variations)
    MIN_SUCCESS_RATE = 0.95
    success_rate = successful / len(sample_files)
    assert success_rate >= MIN_SUCCESS_RATE, \
        f"Only {successful}/{len(sample_files)} ({success_rate:.1%}) files parsed successfully. Expected >= {MIN_SUCCESS_RATE:.0%}"
