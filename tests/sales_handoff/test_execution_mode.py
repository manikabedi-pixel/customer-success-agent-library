import sys

from agents.sales_handoff import ai_main


def test_default_mode_is_mock(
    monkeypatch,
    capsys,
):
    """
    Ensure the default execution mode does not
    invoke the live OpenAI extraction function.
    """

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "Live OpenAI extraction was called in mock mode!"
        )

    monkeypatch.setattr(
        ai_main,
        "extract_sales_intelligence",
        fail_if_called,
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["ai_main"],
    )

    ai_main.main()

    output = capsys.readouterr().out

    assert "Execution mode: MOCK" in output

    assert "OpenAI API calls: NONE" in output