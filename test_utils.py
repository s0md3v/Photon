import pytest
import tld.exceptions
from core.utils import top_level

def test_top_level_with_https_url():
    assert top_level('https://google.co.uk') == 'google.co.uk'
    assert top_level('https://google.com') == 'google.com'

def test_top_level_with_one_level_domain():
    assert top_level('google.co.uk') == 'google.co.uk'
    assert top_level('google.com') == 'google.com'

def test_top_level_with_second_level_domain():
    assert top_level('123.google.co.uk') == 'google.co.uk'
    assert top_level('123.google.com') == 'google.com'

def test_top_level_with_wrong_domain():
    with pytest.raises(tld.exceptions.TldDomainNotFound):
        top_level('google.co.uk2')
