import pytest

from gengowatcher.browser_worker.flows.accept_flow import (
    extract_workbench_payload,
    is_workbench_url,
    normalize_workbench_envelope,
    parse_workbench_job_id,
)


def test_is_workbench_url_detects_success_destination():
    assert is_workbench_url("https://gengo.com/t/workbench/10000003#!/") is True
    assert is_workbench_url("https://gengo.com/t/jobs/details/10000003") is False


def test_is_workbench_url_requires_expected_origin():
    expected = "http://127.0.0.1:8765/t/jobs/details/10000003"

    assert (
        is_workbench_url(
            "http://127.0.0.1:8765/t/workbench/10000003#!/",
            expected_job_id="10000003",
            expected_origin=expected,
        )
        is True
    )
    assert (
        is_workbench_url(
            "https://evil.example/t/workbench/10000003#!/",
            expected_job_id="10000003",
            expected_origin=expected,
        )
        is False
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://gengo.com/prefix/t/workbench/10000003",
        "https://gengo.com/t/workbench/10000003/suffix",
    ],
)
def test_parse_workbench_job_id_rejects_non_exact_paths(url):
    assert parse_workbench_job_id(url) is None


def test_parse_workbench_job_id_extracts_expected_identifier():
    assert (
        parse_workbench_job_id("https://gengo.com/t/workbench/10000003#!/")
        == "10000003"
    )


def test_normalize_workbench_envelope_accepts_gengo_shape():
    payload = {
        "source": "window.__GENGO_WORKBENCH_DATA__",
        "payload": {
            "summary": {
                "order_id": 3000003,
                "expire_time": 1782760306560,
                "seconds_left": 6344,
            },
            "jobs": [{"id": 20000003, "unit_count": 263}],
        },
    }

    assert normalize_workbench_envelope(payload) == payload


@pytest.mark.asyncio
async def test_extract_workbench_payload_uses_page_visible_data():
    payload = {
        "source": "window.__GENGO_WORKBENCH_DATA__",
        "payload": {
            "summary": {"order_id": 3000003, "seconds_left": 6344},
            "jobs": [{"id": 20000003}],
        },
    }

    class FakePage:
        async def evaluate(self, _script):
            return payload

    assert await extract_workbench_payload(FakePage()) == payload
