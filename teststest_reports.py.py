import pandas as pd

def test_csv_export_generation():
    """Test Pandas CSV formatting."""
    df = pd.DataFrame([{"code": "BLD-01", "name": "AeroTech HQ"}])
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    assert len(csv_bytes) > 0