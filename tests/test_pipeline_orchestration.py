import json
from pathlib import Path
from pipeline.catalog import CATALOG, validate_catalog
from pipeline.checkpoints import write_checkpoint, read_checkpoint

def test_catalog_has_twenty_stages():
    assert len(CATALOG) == 20
    assert set(CATALOG) == {"00","01","01a","01b","02","03","04","05","06","07","08","09a","10","11","12","13","14","15","16","17"}

def test_catalog_valid(): assert validate_catalog() == []

def test_checkpoint_is_atomic_and_readable(tmp_path):
    write_checkpoint(tmp_path, "00", {"state":"succeeded"})
    assert read_checkpoint(tmp_path, "00")["state"] == "succeeded"
    assert not list((tmp_path / "stages" / "00").glob("*.tmp"))
