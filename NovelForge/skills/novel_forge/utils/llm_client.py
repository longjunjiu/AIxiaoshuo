"""
LLM客户端 - 支持多种LLM提供商
"""

import os
import json
from typing import Optional, List, Dict, Any, Iterator
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM响应"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class LLMClient:
    """LLM客户端，支持多种提供商"""
    
    def __init__(
        self,
        config,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.provider = provider or config.llm_provider or "openai"
        self.api_key = api_key or config.api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or config.base_url or "https://api.openai.com/v1"
        self.model = model or config.model or "gpt-4"
        self.temperature = getattr(config, 'temperature', 0.7)
        self.max_tokens = getattr(config, 'max_tokens', 4096)
        
        self._client = self._init_client()
    
    def _init_client(self):
        """初始化客户端"""
        if self.provider == "openai":
            try:
                from openai import OpenAI
                return OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                return None
        elif self.provider == "anthropic":
            try:
                import anthropic
                return anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                return None
        else:
            return None
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            system: 系统提示
            temperature: 温度
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            LLMResponse对象
        """
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens
        
        if system:
            messages = [{"role": "system", "content": system}] + messages
        
        if self.provider == "openai" and self._client:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                finish_reason=response.choices[0].finish_reason
            )
        
        elif self.provider == "anthropic" and self._client:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
                system=system,
                **kwargs
            )
            return LLMResponse(
                content=response.content[0].text,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                finish_reason=response.stop_reason
            )
        
        elif self.provider == "custom":
            return self._custom_chat(messages, temperature, max_tokens)
        
        else:
            raise ValueError(f"不支持的LLM提供商: {self.provider}")
    
    def _custom_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """自定义LLM请求（用于兼容其他API）"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        
        return LLMResponse(
            content=result["choices"][0]["message"]["content"],
            model=result.get("model", self.model),
            usage=result.get("usage", {}),
            finish_reason=result["choices"][0].get("finish_reason", "stop")
        )
    
    def stream(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        流式请求
        
        Args:
            messages: 消息列表
            system: 系统提示
            temperature: 温度
            max_tokens: 最大token数
            
        Yields:
            生成的文本片段
        """
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens
        
        if system:
            messages = [{"role": "system", "content": system}] + messages
        
        if self.provider == "openai" and self._client:
            stream = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        elif self.provider == "anthropic" and self._client:
            with self._client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
                system=system,
                **kwargs
            ) as stream:
                for text in stream.text_stream:
                    yield text
        
        else:
            response = self.chat(messages, system, temperature, max_tokens)
            yield response.content
    
    def count_tokens(self, text: str) -> int:
        """估算token数量（简单方法）"""
        return len(text) // 4
    
    def truncate_context(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 3000
    ) -> List[Dict[str, str]]:
        """截断上下文以适应token限制"""
        truncated = []
        current_tokens = 0
        
        for msg in reversed(messages):
            msg_tokens = self.count_tokens(msg.get("content", ""))
            if current_tokens + msg_tokens > max_tokens:
                break
            truncated.insert(0, msg)
            current_tokens += msg_tokens
        
        return truncated


def create_llm_client(
    provider: str = "openai",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: str = "gpt-4"
) -> LLMClient:
    """工厂函数：创建LLM客户端"""
    from dataclasses import dataclass
    
    @dataclass
    class SimpleConfig:
        llm_provider: str = provider
        api_key: str = api_key or ""
        base_url: str = base_url or ""
        model: str = model
        temperature: float = 0.7
        max_tokens: int = 4096
    
    return LLMClient(SimpleConfig())
