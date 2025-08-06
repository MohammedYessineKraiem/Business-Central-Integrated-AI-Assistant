using Microsoft.Extensions.Options;
using System.Text;
using System.Text.Json;
using XPilotCopilotAPI.DTOs;
using XPilotCopilotAPI.Models;

namespace XPilotCopilotAPI.Services
{
    public class ChatService
    {
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;
        private readonly LLMSettings _llmSettings;
        private readonly ModelRouter _modelRouter;


        public ChatService(HttpClient httpClient, IOptions<LLMSettings> llmSettings, ModelRouter modelRouter, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _llmSettings = llmSettings.Value;
            _modelRouter = modelRouter;
            _configuration = configuration;
        }

        public async Task<PromptResponseDTO> GetChatResponseAsync(PromptRequestDTO input)
        {

            var provider = _modelRouter.GetProviderByModel(input.ModelName);

            if (provider == null)
            {
                return new PromptResponseDTO
                {
                    Response = $"Model '{input.ModelName}' is not supported.",
                    ModelUsed = input.ModelName,
                    Status = "error"
                };
            }

            try
            {
                input.Prompt = BuildPromptWithChatContext(input.Prompt ?? "", input.Context ?? "");
                var requestBody = BuildRequestBody(input, provider);
                Console.WriteLine($"[DEBUG] Request body: {requestBody}");

                var request = new HttpRequestMessage(HttpMethod.Post, provider.BaseUrl);

                if (provider.RequiresKey)
                {
                    if (string.IsNullOrWhiteSpace(provider.ApiKey))
                    {
                        return new PromptResponseDTO
                        {
                            Response = $"API key not found for {provider.Name}. Check your secrets.",
                            ModelUsed = provider.Model,
                            Status = "error"
                        };
                    }
                    if (provider.RequiresKey && !string.IsNullOrWhiteSpace(provider.ApiKey))
                    {
                        if (provider.Provider.ToLower() == "anthropic")
                        {
                            // Anthropic uses different header format and needs version header
                            request.Headers.Add("x-api-key", provider.ApiKey);
                            request.Headers.Add("anthropic-version", "2023-06-01");
                        }
                        else
                        {
                            // All other providers use Bearer token
                            request.Headers.Add("Authorization", $"Bearer {provider.ApiKey}");
                        }
                    }

                }

                request.Content = new StringContent(requestBody, Encoding.UTF8, "application/json");

                var response = await _httpClient.SendAsync(request);

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();

                    Console.WriteLine($"[DEBUG] Error response: {errorContent}");
                    return new PromptResponseDTO
                    {
                        Response = $"Error from LLM provider: {(int)response.StatusCode} {response.ReasonPhrase} - {errorContent}",
                        ModelUsed = provider.Model,
                        Status = "error"
                    };
                }

                var responseContent = await response.Content.ReadAsStringAsync();

                var answer = ParseLLMResponse(responseContent, provider);

                return new PromptResponseDTO
                {
                    Response = answer,
                    ModelUsed = provider.Model,
                    Status = "success"
                };
            }
            catch (Exception ex)
            {
                return new PromptResponseDTO
                {
                    Response = $"Exception: {ex.Message}",
                    ModelUsed = provider.Model,
                    Status = "error"
                };
            }
        }


        private string BuildPromptWithChatContext(string userPrompt, string chatContext)
        {
            var systemContext = @"
You are an AI assistant specialized in generating structured commands and clear vision and comprehension for Microsoft Dynamics 365 Business Central and anything
to do with its foundationd development coding and extensions.
for further context to what the user has been on lately you will be provided with a chat context that is the last 5 requests the user did 
keep the responses under 2048 characters if possible. dont overburden the user with referring to past context youre the only one that has access to it just to 
aid you answer better so you dont really have to use it when the user alternate the subject of the conversation. You can alse answer some questions that are not related to business central but you must always refer to the user prompt and the chat context to answer the user question.
You must consider the user’s recent interactions below when answering the next command:
Recent user activity (last 5 requests):
" + chatContext + @"

Now, process the following user command carefully:
";

            return $"{systemContext}\nUser command: {userPrompt}";
        }


        private string BuildRequestBody(PromptRequestDTO input, LLMProviderConfig provider)
        {
            switch (provider.Provider.ToLower())
            {
                case "openai":
                    var openAiPayload = new
                    {
                        model = provider.ModelName,
                        messages = new[]
                        {
                    new { role = "user", content = input.Prompt }
                },
                        temperature = 0.7, // Example parameter, adjust as needed
                        max_tokens = 1000, // Example parameter, adjust as needed

                        // Add context or other parameters if needed
                    };
                    Console.WriteLine($"[DEBUG] OpenAI request body: {JsonSerializer.Serialize(openAiPayload)}");
                    return JsonSerializer.Serialize(openAiPayload);

                case "anthropic":
                    var anthropicPayload = new
                    {
                        model = provider.ModelName,
                        max_tokens = 1000,
                        messages = new[]
                        {
                    new { role = "user", content = input.Prompt }
                },
                        system = "You are a helpful assistant." // Add this
                    };
                    var json = JsonSerializer.Serialize(anthropicPayload);
                    Console.WriteLine($"[DEBUG] Anthropic request body: {json}");
                    return json;

                case "mistral":
                case "together":
                case "groq":
                    var genericPayload = new
                    {
                        model = provider.ModelName,
                        messages = new[]
                        {
                    new { role = "user", content = input.Prompt }
                }
                    };
                    return JsonSerializer.Serialize(genericPayload);

                default:
                    return JsonSerializer.Serialize(new { prompt = input.Prompt });
            }
        }


        private string ParseLLMResponse(string responseContent, LLMProviderConfig provider)
        {
            try
            {
                using JsonDocument doc = JsonDocument.Parse(responseContent);

                switch (provider.Provider.ToLower())
                {
                    case "openai":
                    case "mistral":
                    case "together":
                    case "groq":
                        if (doc.RootElement.TryGetProperty("choices", out JsonElement choices) &&
                            choices.GetArrayLength() > 0)
                        {
                            var message = choices[0].GetProperty("message");
                            if (message.TryGetProperty("content", out JsonElement content))
                            {
                                return content.GetString() ?? "No content";
                            }
                        }
                        break;

                    case "anthropic":
                        if (doc.RootElement.TryGetProperty("completion", out JsonElement completion))
                        {
                            return completion.GetString() ?? "No completion";
                        }
                        break;

                    default:
                        return responseContent.Length > 500 ? responseContent.Substring(0, 500) + "..." : responseContent;
                }
            }
            catch (JsonException)
            {
                return "Failed to parse LLM response JSON.";
            }
            catch (Exception ex)
            {
                return $"Exception during parsing: {ex.Message}";
            }

            return "No valid answer found in LLM response.";
        }
    }
}
