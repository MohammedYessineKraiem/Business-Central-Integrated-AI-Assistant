using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Options;
using XPilotCopilotAPI.DTOs;
using XPilotCopilotAPI.Models;

namespace XPilotCopilotAPI.Services
{
    public class IntentParserService : IIntentParserService
    {
        private readonly HttpClient _httpClient;
        private readonly LLMSettings _llmSettings;
        private readonly ModelRouter _modelRouter;
        private readonly IConfiguration _configuration;

        private const string SystemContext = @"
You are a Business Central Copilot.
Classify the user prompt into one of two types:
- If it’s a question or informational query, return: Question
- If it’s an action request (create, update, delete), return: Command
Return only one word: 'Command' or 'Question'.
User prompt:
";

        public IntentParserService(HttpClient httpClient, IOptions<LLMSettings> llmSettings, ModelRouter modelRouter, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _llmSettings = llmSettings.Value;
            _modelRouter = modelRouter;
            _configuration = configuration;
        }

        public async Task<PromptClassificationResponseDTO> ClassifyPromptAsync(string prompt, string model)
        {
            var provider = _modelRouter.GetProviderByModel(model);

            if (provider == null || string.IsNullOrEmpty(provider.BaseUrl))
                return new PromptClassificationResponseDTO { Type = "Question" };

            string fullPrompt = BuildFullPromptWithContext(prompt);

            var requestBody = BuildRequestBody(fullPrompt, provider);
            var request = new HttpRequestMessage(HttpMethod.Post, provider.BaseUrl);

            if (provider.RequiresKey && !string.IsNullOrWhiteSpace(provider.ApiKey))
            {
                if (provider.Provider.ToLower() == "anthropic")
                {
                    request.Headers.Add("x-api-key", provider.ApiKey);
                    request.Headers.Add("anthropic-version", "2023-06-01");
                }
                else
                {
                    request.Headers.Add("Authorization", $"Bearer {provider.ApiKey}");
                }
            }

            request.Content = new StringContent(requestBody, Encoding.UTF8, "application/json");

            try
            {
                var response = await _httpClient.SendAsync(request);
                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();

                    Console.WriteLine($"[DEBUG] Error response: {errorContent}");
                    return new PromptClassificationResponseDTO
                    {
                      Type = "Question",
                    };
                }
                var responseContent = await response.Content.ReadAsStringAsync();

                var classification = ParseClassification(responseContent, provider);
                return new PromptClassificationResponseDTO { Type = classification };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[INTENT ERROR] {ex.Message}");
                return new PromptClassificationResponseDTO { Type = "Question" };
            }
        }

        private string BuildFullPromptWithContext(string userPrompt)
        {
            return $"{SystemContext}{userPrompt}";
        }

        private string BuildRequestBody(string fullPrompt, LLMProviderConfig provider)
        {
            var userMessage = new[]
            {
                new { role = "user", content = fullPrompt }
            };

            switch (provider.Provider.ToLower())
            {
                case "openai":
                case "groq":
                case "mistral":
                case "together":
                    return JsonSerializer.Serialize(new
                    {
                        model = provider.ModelName,
                        messages = userMessage,
                        temperature = 0,
                        max_tokens = 10
                    });

                case "anthropic":
                    return JsonSerializer.Serialize(new
                    {
                        model = provider.ModelName,
                        max_tokens = 1000,
                        messages = userMessage,
                        system = "You are a helpful assistant. Return only 'Command' or 'Question'."
                    });

                default:
                    return JsonSerializer.Serialize(new { prompt = fullPrompt });
            }
        }

        private string NormalizeClassification(string? raw)
        {
            if (string.IsNullOrWhiteSpace(raw))
                return "Question";

            var lower = raw.Trim().ToLowerInvariant();
            if (lower.Contains("command"))
                return "Command";
            return "Question";
        }

        private string ParseClassification(string responseContent, LLMProviderConfig provider)
        {
            try
            {
                using var doc = JsonDocument.Parse(responseContent);
                var providerName = provider.Provider.ToLower();

                if (providerName == "openai" || providerName == "groq" || providerName == "mistral" || providerName == "together")
                {
                    var content = doc.RootElement.GetProperty("choices")[0].GetProperty("message").GetProperty("content").GetString();
                    return NormalizeClassification(content);
                }

                if (providerName == "anthropic")
                {
                    var completion = doc.RootElement.GetProperty("completion").GetString();
                    return NormalizeClassification(completion);
                }

                // fallback to raw content normalized
                return NormalizeClassification(responseContent);
            }
            catch
            {
                return "Question"; // fallback classification on error
            }
        }
    }
}
