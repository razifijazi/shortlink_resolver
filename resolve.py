import re
import sys
import time
from urllib.parse import urljoin, urlparse

import requests

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'


def extract_form(html, form_id):
    m = re.search(rf'<form[^>]*id=["\']{form_id}["\'][^>]*action=["\']([^"\']+)["\'][^>]*>(.*?)</form>', html, re.I | re.S)
    if not m:
        return None, {}
    action = m.group(1)
    frag = m.group(2)
    data = {}
    for tag in re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', frag, re.I):
        name = re.search(r'name=["\']([^"\']+)', tag, re.I)
        value = re.search(r'value=["\']([^"\']*)', tag, re.I)
        if name:
            data[name.group(1)] = value.group(1) if value else ''
    return action, data


def resolve(url):
    parsed = urlparse(url)
    base = f'{parsed.scheme}://{parsed.netloc}'

    s = requests.Session()
    headers = {'User-Agent': UA, 'Referer': url}

    r = s.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    html = r.text

    # JS on site sets/updates adblock cookie state. We mimic pass state.
    s.cookies.set('ab', '1', domain=parsed.netloc, path='/')

    go_action, go_data = extract_form(html, 'go-link')
    popup_action, popup_data = extract_form(html, 'go-popup')

    if not go_action or not go_data:
        raise RuntimeError('go-link form not found')

    # Important: popup form is part of the required state for this site.
    if popup_action and popup_data:
        s.post(
            urljoin(base + '/', popup_action),
            data=popup_data,
            headers={
                **headers,
                'Origin': base,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            },
            timeout=30,
            allow_redirects=False,
        )

    timer = re.search(r'<span id=["\']timer["\'][^>]*>\s*(\d+)\s*<', html, re.I)
    wait_seconds = int(timer.group(1)) if timer else 0
    if wait_seconds:
        time.sleep(min(wait_seconds, 10))

    resp = s.post(
        urljoin(base + '/', go_action),
        data=go_data,
        headers={
            **headers,
            'Origin': base,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
        },
        timeout=30,
    )
    resp.raise_for_status()

    data = resp.json()
    if isinstance(data, dict) and data.get('url'):
        return data['url']

    raise RuntimeError(f'Unexpected response: {data}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 resolve.py <shortlink>')
        sys.exit(1)
    try:
        final = resolve(sys.argv[1])
        print(final)
    except Exception as e:
        print(f'ERROR: {e}')
        sys.exit(2)
