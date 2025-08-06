/*
🔹 1. OpenAI (GPT-4, GPT-3.5)
Models: gpt-4, gpt-4-turbo, gpt-3.5-turbo

Source: https://platform.openai.com

How to Get API Key: Sign up > Go to API keys > Create key

Pricing: Pay-as-you-go (some free trials)

Endpoint: https://api.openai.com/v1/chat/completions

Key Needed? ✅ Yes

🔹 2. Anthropic (Claude 3 series)
Models: claude-3-opus, claude-3-sonnet, claude-3-haiku

Source: https://console.anthropic.com

How to Get API Key: Create account > View API keys

Pricing: Pay-as-you-go

Endpoint: https://api.anthropic.com/v1/messages

Key Needed? ✅ Yes

🔹 3. Mistral (OpenWeight & Paid)
Models: mistral-tiny, mistral-small, mistral-medium

Source: https://console.mistral.ai

How to Get API Key: Register > Get key

Endpoint: https://api.mistral.ai/v1/chat/completions

Key Needed? ✅ Yes

🔹 4. Together AI (Aggregator Platform)
Models: LLaMA 2/3, Mistral, Mixtral, Yi, etc.

Source: https://www.together.ai

How to Get API Key: Sign up > Get API key

Endpoint: https://api.together.xyz/v1/chat/completions

Key Needed? ✅ Yes

Notes: Runs many open models for free or at low cost

🔹 5. Groq (Ultra-fast LLaMA3 / Mixtral)
Models: llama3-8b, mixtral-8x7b

Source: https://console.groq.com

How to Get API Key: Sign up > Create Key

Endpoint: https://api.groq.com/openai/v1/chat/completions

Key Needed? ✅ Yes

Notes: Optimized for speed using LPU hardware

🔹 6. Ollama (Self-hosted Local Models)
Models: mistral, llama3, codellama, gemma, etc.

Source: https://ollama.com

How to Get It:

Download Ollama

Run ollama pull mistral

Start Ollama (it runs at localhost:11434)

Endpoint: http://localhost:11434/api/chat

Key Needed? ❌ No key required

Notes: Best for private/offline dev

🔹 7. LM Studio (Desktop LLM API Server)
Models: Any GGUF model (e.g. llama3, phi-2)

Source: https://lmstudio.ai

How to Get It:

Install LM Studio (GUI)

Load any compatible model

Enable local API server

Endpoint: http://localhost:1234/v1/chat/completions (configurable)

Key Needed? ❌ No

Notes: Ideal for non-dev users or quick API testing

🔹 8. LocalAI (Docker-based Open Source LLM API)
Models: LLaMA, Mistral, RWKV, etc.

Source: https://github.com/go-skynet/LocalAI

How to Get It:

Use Docker: docker run -p 8080:8080 localai/localai

Mount models or download them directly

Endpoint: http://localhost:8080/v1/chat/completions

Key Needed? ❌ No

Notes: Best for full control & automation in self-hosted stacks

*/



enum 50100 "AI Model"
{
    Extensible = false;
    Caption = 'AI Model';

    value(0; GPT35Turbo)
    {
        Caption = 'gpt-3.5-turbo';
    }
    value(1; Claude3)
    {
        Caption = 'claude-3';
    }
    value(2; Mistral7B)
    {
        Caption = 'mistral-7b';
    }
    value(3; TogetherAI)
    {
        Caption = 'together-ai';
    }
    value(4; Groq)
    {
        Caption = 'groq';
    }

}
