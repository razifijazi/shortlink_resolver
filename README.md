# shortlink_resolver

Resolver HTTP sederhana untuk shortlink model interstitial + form submit.

## Scope awal
- Domain mirip `savetub.com`
- Flow: GET page -> parse hidden inputs -> POST `/links/go` -> ambil hasil

## Usage
```bash
cd ~/.openclaw/workspace/shortlink_resolver
python3 resolve.py 'https://savetub.com/u4O54dM'
```
