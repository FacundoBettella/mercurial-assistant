import pytest
from unittest.mock import AsyncMock
from src.application.pipeline.pipeline import Pipeline
from src.application.pipeline.context import ProcessingState
from src.domain.entities.moderation_request import ModerationRequest


def make_state() -> ProcessingState:
    return ProcessingState(
        request=ModerationRequest(user_id="u1", text="test ticket"),
        system_prompt="sys",
        model="gpt-4o-mini",
    )


def step_that_passes(extra=None):
    """Returns an AsyncMock step that forwards state unchanged."""
    mock = AsyncMock()
    async def passthrough(state):
        return state
    mock.process.side_effect = passthrough
    return mock


def step_that_blocks():
    """Returns an AsyncMock step that stops the pipeline."""
    mock = AsyncMock()
    async def block(state):
        state.stop_pipeline("blocked by test")
        return state
    mock.process.side_effect = block
    return mock


async def test_all_steps_are_executed_in_order():
    calls = []

    def make_step(name):
        mock = AsyncMock()
        async def process(state):
            calls.append(name)
            return state
        mock.process.side_effect = process
        return mock

    pipeline = Pipeline(steps=[make_step("first"), make_step("second"), make_step("third")])
    await pipeline.execute(make_state())

    assert calls == ["first", "second", "third"]


async def test_pipeline_stops_after_blocked_step():
    step1 = step_that_blocks()
    step2 = step_that_passes()

    pipeline = Pipeline(steps=[step1, step2])
    result = await pipeline.execute(make_state())

    step2.process.assert_not_called()
    assert result.blocked is True
    assert result.should_continue is False


async def test_pipeline_returns_final_state():
    step = step_that_passes()
    pipeline = Pipeline(steps=[step])
    state = make_state()

    result = await pipeline.execute(state)

    assert result is state


async def test_empty_pipeline_returns_state_unchanged():
    pipeline = Pipeline(steps=[])
    state = make_state()
    result = await pipeline.execute(state)
    assert result is state
    assert result.blocked is False
