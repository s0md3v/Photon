import requests
from core.utils import is_link

def u_test_is_link():
    assert not (is_link("anyCharactersThatDontEndWithBAD_TYPES", [], [])) # faulty URL
    assert not (is_link("", [], [])) # empty string
    assert not (is_link("     ", [], [])) # whitespace only
    assert not (is_link(";&&#!!!!", [], [])) # special characters
    assert (is_link("http://www.example.com", [], [])) # valid link
    assert (is_link("https://github.com/viliau", [], [])) # valid link


if __name__ == "__main__":
    u_test_is_link()