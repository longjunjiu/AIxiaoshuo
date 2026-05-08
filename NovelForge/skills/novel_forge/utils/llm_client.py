"""
LLM客户端 - 支持多种LLM提供商和本地模型
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
    """LLM客户端，支持多种提供商和本地模型"""
    
    SUPPORTED_PROVIDERS = [
        "openai", "anthropic", "custom", 
        "huggingface", "ollama", "api2d",
        "deepseek", "qwen", "zhipu", "nvidia"
    ]
    
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
        self.base_url = base_url or config.base_url or self._get_default_base_url()
        self.model = model or config.model or self._get_default_model()
        self.temperature = getattr(config, 'temperature', 0.7)
        self.max_tokens = getattr(config, 'max_tokens', 4096)
        self.top_p = getattr(config, 'top_p', 0.9)
        self.frequency_penalty = getattr(config, 'frequency_penalty', 0.0)
        self.presence_penalty = getattr(config, 'presence_penalty', 0.0)
        
        self._client = None
        self._hf_pipeline = None
        self._init_client()
    
    def _get_default_base_url(self) -> str:
        """获取默认base_url"""
        defaults = {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com/v1",
            "custom": "http://localhost:8000/v1",
            "huggingface": "https://api-inference.huggingface.co/models",
            "ollama": "http://localhost:11434/v1",
            "api2d": "https://api2d.com/v1",
            "deepseek": "https://api.deepseek.com/v1",
            "qwen": "https://api.qwenlm.com/v1",
            "zhipu": "https://open.bigmodel.cn/api/paas/v4",
            "nvidia": "https://integrate.api.nvidia.com/v1"
        }
        return defaults.get(self.provider, "https://api.openai.com/v1")
    
    def _get_default_model(self) -> str:
        """获取默认模型"""
        defaults = {
            "openai": "gpt-4",
            "anthropic": "claude-3-opus-20240229",
            "custom": "gpt-4",
            "huggingface": "meta-llama/Llama-2-7b-chat-hf",
            "ollama": "llama3",
            "api2d": "gpt-4",
            "deepseek": "deepseek-chat",
            "qwen": "qwen-plus",
            "zhipu": "glm-4",
            "nvidia": "meta/llama-3.1-70b-instruct"
        }
        return defaults.get(self.provider, "gpt-4")
    
    def _init_client(self):
        """初始化客户端"""
        if self.provider == "openai":
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                pass
        elif self.provider == "anthropic":
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                pass
        elif self.provider == "ollama":
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key="ollama", base_url=self.base_url)
            except ImportError:
                pass
        elif self.provider == "api2d":
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                pass
        elif self.provider == "deepseek":
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                pass
        elif self.provider == "qwen":
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                pass
        elif self.provider == "zhipu":
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                pass
        elif self.provider == "huggingface":
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
                self._tokenizer = AutoTokenizer.from_pretrained(self.model)
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model,
                    device_map="auto",
                    load_in_4bit=True if "7b" in self.model.lower() else False
                )
                self._hf_pipeline = pipeline(
                    "text-generation",
                    model=self._model,
                    tokenizer=self._tokenizer,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature,
                    do_sample=True
                )
            except ImportError:
                pass
        elif self.provider == "custom":
            pass
    
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
        temp = temperature or self.temperature
        mt = max_tokens or self.max_tokens
        
        if self.provider == "anthropic":
            return self._chat_anthropic(messages, system, temp, mt, **kwargs)
        elif self.provider == "huggingface":
            return self._chat_huggingface(messages, system, temp, mt, **kwargs)
        elif self.provider in ["openai", "ollama", "api2d", "deepseek", "qwen", "zhipu", "custom"]:
            return self._chat_openai_compatible(messages, system, temp, mt, **kwargs)
        else:
            raise ValueError(f"不支持的LLM提供商: {self.provider}")
    
    def _chat_openai_compatible(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> LLMResponse:
        """OpenAI兼容API聊天"""
        if system:
            messages = [{"role": "system", "content": system}] + messages
        
        if not self._client:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": self.top_p,
                **kwargs
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            
            return LLMResponse(
                content=result["choices"][0]["message"]["content"],
                model=result.get("model", self.model),
                usage=result.get("usage", {}),
                finish_reason=result["choices"][0].get("finish_reason", "stop")
            )
        
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=self.top_p,
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
    
    def _chat_anthropic(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> LLMResponse:
        """Anthropic API聊天"""
        if self._client:
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
        else:
            import requests
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages,
                "system": system,
                **kwargs
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            
            return LLMResponse(
                content=result["content"][0]["text"],
                model=result.get("model", self.model),
                usage=result.get("usage", {}),
                finish_reason=result.get("stop_reason", "stop")
            )
    
    def _chat_huggingface(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> LLMResponse:
        """Hugging Face本地模型聊天"""
        if self._hf_pipeline:
            conversation = ""
            if system:
                conversation += f"System: {system}\n"
            
            for msg in messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation += f"{role}: {msg['content']}\n"
            
            conversation += "Assistant:"
            
            outputs = self._hf_pipeline(
                conversation,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                **kwargs
            )
            
            response_text = outputs[0]["generated_text"].replace(conversation, "").strip()
            
            return LLMResponse(
                content=response_text,
                model=self.model,
                usage={},
                finish_reason="stop"
            )
        else:
            raise RuntimeError("Hugging Face pipeline未初始化")
    
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
        temp = temperature or self.temperature
        mt = max_tokens or self.max_tokens
        
        if self.provider == "anthropic" and self._client:
            with self._client.messages.stream(
                model=self.model,
                max_tokens=mt,
                temperature=temp,
                messages=messages,
                system=system,
                **kwargs
            ) as stream:
                for text in stream.text_stream:
                    yield text
        elif self.provider in ["openai", "ollama", "api2d", "deepseek", "qwen", "zhipu"] and self._client:
            stream = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system}] + messages if system else messages,
                temperature=temp,
                max_tokens=mt,
                stream=True,
                **kwargs
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            response = self.chat(messages, system, temp, mt)
            yield response.content
    
    def count_tokens(self, text: str) -> int:
        """估算token数量"""
        try:
            import tiktoken
            encoder = tiktoken.encoding_for_model(self.model)
            return len(encoder.encode(text))
        except:
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
    model: str = "gpt-4",
    **kwargs
) -> LLMClient:
    """工厂函数：创建LLM客户端"""
    from dataclasses import dataclass
    
    @dataclass
    class SimpleConfig:
        llm_provider: str = provider
        api_key: str = api_key or ""
        base_url: str = base_url or ""
        model: str = model
        temperature: float = kwargs.get('temperature', 0.7)
        max_tokens: int = kwargs.get('max_tokens', 4096)
        top_p: float = kwargs.get('top_p', 0.9)
        frequency_penalty: float = kwargs.get('frequency_penalty', 0.0)
        presence_penalty: float = kwargs.get('presence_penalty', 0.0)
    
    return LLMClient(SimpleConfig())


def list_supported_providers() -> List[str]:
    """列出支持的提供商"""
    return LLMClient.SUPPORTED_PROVIDERS
