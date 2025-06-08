from datetime import datetime
from youtube_api_get import extract_channel_id_from_url
test_cases = [
    # (input_url, expected_output)
    ('https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw', 'UC_x5XG1OV2P6uZZ5FSM9Ttw'),
    ('https://www.youtube.com/@GoogleDevelopers', 'APIで解決される値'),
    ('https://www.youtube.com/c/GoogleDevelopers', 'APIで解決される値'),
    ('https://www.youtube.com/user/GoogleDevelopers', 'APIで解決される値'),
    ('invalid_url', None),
    ('', None),
]
    
for url, expected in test_cases:
    result = extract_channel_id_from_url(url)
    print(f"URL: {url} -> {result} (expected: {expected})")
