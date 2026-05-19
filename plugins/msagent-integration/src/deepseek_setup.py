"""Register the ``deepseek`` provider with msagent and ensure ``reasoning_content``
is preserved across multi-turn conversations.

DeepSeek's thinking mode is **enabled by default**.  The API returns
``reasoning_content`` on every assistant message and requires it to be passed
back in subsequent requests (400 otherwise).

``langchain-deepseek``'s ``ChatDeepSeek`` handles the **response** side
correctly by storing ``reasoning_content`` in ``additional_kwargs``, but its
``_get_request_payload`` does not pass it back in **requests**.  We override
that one method — which is explicitly designed for payload customization — at
the class level.

We also add ``deepseek`` to msagent's provider maps so that
``init_chat_model("deepseek:...")`` is used instead of the generic
``ChatOpenAI`` + base_url workaround.
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage


def setup() -> None:
    """Call once before creating the agent graph."""
    _register_deepseek_provider()
    _patch_chat_deepseek_get_request_payload()


# ── msagent provider registration ────────────────────────────────────────────


def _register_deepseek_provider() -> None:
    """Add ``deepseek`` to msagent's LLM provider maps."""
    import msagent.configs.llm as _llm
    import msagent.llms.factory as _f

    # init_chat_model already supports deepseek — msagent just doesn't know about it
    _f._SUPPORTED_PROVIDER_MAP["deepseek"] = "deepseek"
    _f._DEFAULT_PROVIDER_API_KEY_ENV["deepseek"] = "OPENAI_API_KEY"
    _f._PROVIDER_API_KEY_KWARG["deepseek"] = "openai_api_key"
    _f._PROVIDER_BASE_URL_KWARG["deepseek"] = "openai_api_base"

    # LLMProvider enum (used by pydantic validation + _filter_supported_llms)
    # doesn't include deepseek.  Without this the deepseek LLM config is
    # silently dropped, the agent gets no model, and the entire tool/skill
    # pipeline is disabled.
    _provider_enum = _llm.LLMProvider
    _ds_member = str.__new__(_provider_enum, "deepseek")
    _ds_member._name_ = "DEEPSEEK"
    _ds_member._value_ = "deepseek"
    _provider_enum._value2member_map_["deepseek"] = _ds_member
    _provider_enum._member_names_.append("DEEPSEEK")
    _provider_enum._member_map_["DEEPSEEK"] = _ds_member


# ── ChatDeepSeek._get_request_payload override ───────────────────────────────


_ORIG_GET_REQUEST_PAYLOAD = None


def _patch_chat_deepseek_get_request_payload() -> None:
    """Override ``ChatDeepSeek._get_request_payload`` to preserve ``reasoning_content``."""
    global _ORIG_GET_REQUEST_PAYLOAD
    if _ORIG_GET_REQUEST_PAYLOAD is not None:
        return  # idempotent

    from langchain_deepseek.chat_models import ChatDeepSeek

    _ORIG_GET_REQUEST_PAYLOAD = ChatDeepSeek._get_request_payload

    def _patched_get_request_payload(
        self: ChatDeepSeek,
        input_: Any,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> dict:
        assert _ORIG_GET_REQUEST_PAYLOAD is not None  # set above
        payload = _ORIG_GET_REQUEST_PAYLOAD(self, input_, stop=stop, **kwargs)
        # Map original messages to payload dicts, injecting reasoning_content
        # where present in the AIMessage's additional_kwargs.
        messages = self._convert_input(input_).to_messages()
        for msg, pl_msg in zip(messages, payload["messages"]):
            if isinstance(msg, AIMessage) and pl_msg.get("role") == "assistant":
                rc = msg.additional_kwargs.get("reasoning_content")
                if rc:
                    pl_msg["reasoning_content"] = rc
        return payload

    ChatDeepSeek._get_request_payload = _patched_get_request_payload
