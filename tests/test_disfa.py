import pytest

from tools.evaluation.disfa import episodes, labels


def test_disfa_indices_and_episode_boundaries():
    values = labels(b"1,0\r\r\n2,2\r\r\n3,5\r\r\n4,1\r\r\n5,3\r\r\n")
    assert episodes(values) == [(1, 3), (4, 5)]
    assert episodes([0, 1, 0]) == []
    for invalid in (b"", b"0,1", b"1,6", b"1,0\n3,2", b"1,0,2"):
        with pytest.raises(ValueError):
            labels(invalid)
