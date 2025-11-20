This directory: `utils/ffuf`

- Required repo: `drill-test-gadget` (this repo)
- Additional repos: none

Installation (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r utils\ffuf\requirements.txt
```

Quick test (import check):

```powershell
python -c "from utils.ffuf import analyze_target; import json; print(json.dumps(analyze_target('http://example.com', samples=1), ensure_ascii=False))"
```

Example usage (from another Python file):

```python
from utils.ffuf import analyze_target
res = analyze_target('http://example.com', samples=4)
print(res)
```

Packages:

- `requests`
- `aiohttp`
