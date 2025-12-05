"""LLM adapters for bridging langchain and llama-index.

This module provides compatibility adapters between langchain 1.x and llama-index,
working around issues with the llama-index-llms-langchain package which still
uses old langchain import paths.
"""

from __future__ import annotations

from typing import Any, Generator, Optional, Sequence

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import AIMessage

from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
    ChatResponseAsyncGen,
    ChatResponseGen,
    CompletionResponse,
    CompletionResponseAsyncGen,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.bridge.pydantic import PrivateAttr
from llama_index.core.callbacks import CallbackManager
from llama_index.core.llms.callbacks import llm_chat_callback, llm_completion_callback
from llama_index.core.base.llms.generic_utils import (
    completion_response_to_chat_response,
    stream_completion_response_to_chat_response,
)
from llama_index.core.llms.llm import LLM
from llama_index.core.types import BaseOutputParser, PydanticProgramMode


class LangChainLLM(LLM):
    """Adapter for a LangChain LLM.
    
    This is a compatibility adapter that works with langchain 1.x,
    replacing the broken llama-index-llms-langchain package.
    
    Examples:
        from langchain_openai import ChatOpenAI
        from app.utils.llm_adapters import LangChainLLM
        
        llm = ChatOpenAI(model="gpt-4")
        llama_llm = LangChainLLM(llm=llm)
    """

    _llm: BaseLanguageModel = PrivateAttr()

    def __init__(
        self,
        llm: BaseLanguageModel,
        callback_manager: Optional[CallbackManager] = None,
        system_prompt: Optional[str] = None,
        messages_to_prompt: Optional[Any] = None,
        completion_to_prompt: Optional[Any] = None,
        pydantic_program_mode: PydanticProgramMode = PydanticProgramMode.DEFAULT,
        output_parser: Optional[BaseOutputParser] = None,
    ) -> None:
        """Initialize the adapter."""
        super().__init__(
            callback_manager=callback_manager,
            system_prompt=system_prompt,
            messages_to_prompt=messages_to_prompt,
            completion_to_prompt=completion_to_prompt,
            pydantic_program_mode=pydantic_program_mode,
            output_parser=output_parser,
        )
        self._llm = llm

    @classmethod
    def class_name(cls) -> str:
        return "LangChainLLM"

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata()

    @llm_completion_callback()
    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        """Complete a prompt."""
        output = self._llm.invoke(prompt, **kwargs)
        if isinstance(output, AIMessage):
            text = output.content
        else:
            text = str(output)
        return CompletionResponse(text=text)

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        """Stream complete a prompt."""
        def gen() -> Generator[CompletionResponse, None, None]:
            for chunk in self._llm.stream(prompt, **kwargs):
                if isinstance(chunk, AIMessage):
                    text = chunk.content
                else:
                    text = str(chunk)
                yield CompletionResponse(text=text, delta=text)
        return gen()

    @llm_chat_callback()
    def chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        """Chat with the model."""
        # Convert llama-index messages to langchain format
        lc_messages = []
        for msg in messages:
            if msg.role == "user":
                from langchain_core.messages import HumanMessage
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                from langchain_core.messages import SystemMessage
                lc_messages.append(SystemMessage(content=msg.content))
            else:
                from langchain_core.messages import HumanMessage
                lc_messages.append(HumanMessage(content=msg.content))
        
        output = self._llm.invoke(lc_messages, **kwargs)
        if isinstance(output, AIMessage):
            text = output.content
        else:
            text = str(output)
        
        return ChatResponse(
            message=ChatMessage(role="assistant", content=text),
        )

    @llm_chat_callback()
    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        """Stream chat with the model."""
        lc_messages = []
        for msg in messages:
            if msg.role == "user":
                from langchain_core.messages import HumanMessage
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                from langchain_core.messages import SystemMessage
                lc_messages.append(SystemMessage(content=msg.content))
            else:
                from langchain_core.messages import HumanMessage
                lc_messages.append(HumanMessage(content=msg.content))
        
        def gen() -> Generator[ChatResponse, None, None]:
            content = ""
            for chunk in self._llm.stream(lc_messages, **kwargs):
                if isinstance(chunk, AIMessage):
                    delta = chunk.content
                else:
                    delta = str(chunk)
                content += delta
                yield ChatResponse(
                    message=ChatMessage(role="assistant", content=content),
                    delta=delta,
                )
        
        return gen()

    async def acomplete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        """Async complete a prompt."""
        output = await self._llm.ainvoke(prompt, **kwargs)
        if isinstance(output, AIMessage):
            text = output.content
        else:
            text = str(output)
        return CompletionResponse(text=text)

    async def achat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        """Async chat with the model."""
        lc_messages = []
        for msg in messages:
            if msg.role == "user":
                from langchain_core.messages import HumanMessage
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                from langchain_core.messages import SystemMessage
                lc_messages.append(SystemMessage(content=msg.content))
            else:
                from langchain_core.messages import HumanMessage
                lc_messages.append(HumanMessage(content=msg.content))
        
        output = await self._llm.ainvoke(lc_messages, **kwargs)
        if isinstance(output, AIMessage):
            text = output.content
        else:
            text = str(output)
        
        return ChatResponse(
            message=ChatMessage(role="assistant", content=text),
        )

    async def astream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseAsyncGen:
        """Async stream complete a prompt."""
        async def gen() -> CompletionResponseAsyncGen:
            async for chunk in self._llm.astream(prompt, **kwargs):
                if isinstance(chunk, AIMessage):
                    text = chunk.content
                else:
                    text = str(chunk)
                yield CompletionResponse(text=text, delta=text)
        return gen()

    async def astream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseAsyncGen:
        """Async stream chat with the model."""
        lc_messages = []
        for msg in messages:
            if msg.role == "user":
                from langchain_core.messages import HumanMessage
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                from langchain_core.messages import SystemMessage
                lc_messages.append(SystemMessage(content=msg.content))
            else:
                from langchain_core.messages import HumanMessage
                lc_messages.append(HumanMessage(content=msg.content))
        
        async def gen() -> ChatResponseAsyncGen:
            content = ""
            async for chunk in self._llm.astream(lc_messages, **kwargs):
                if isinstance(chunk, AIMessage):
                    delta = chunk.content
                else:
                    delta = str(chunk)
                content += delta
                yield ChatResponse(
                    message=ChatMessage(role="assistant", content=content),
                    delta=delta,
                )
        return gen()


__all__ = ["LangChainLLM"]

