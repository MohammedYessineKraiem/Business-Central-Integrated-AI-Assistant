using XPilotCopilotAPI.DTOs;
using XPilotCopilotAPI.Models;
using Microsoft.Extensions.Options;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System;
using System.Collections.Generic;
using Microsoft.Extensions.Logging;

namespace XPilotCopilotAPI.Services
{
    public class LlmService : ILlmService
    {
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;
        private readonly LLMSettings _llmSettings;
        private readonly ModelRouter _modelRouter;
        private readonly ILogger<LlmService> _logger;

        public LlmService(
            HttpClient httpClient,
            IOptions<LLMSettings> llmSettings,
            ModelRouter modelRouter,
            IConfiguration configuration,
            ILogger<LlmService> logger)
        {
            _httpClient = httpClient;
            _llmSettings = llmSettings.Value;
            _modelRouter = modelRouter;
            _configuration = configuration;
            _logger = logger;
        }

        public async Task<CommandParsedDTO> ParseCommandAsync(string prompt, string modelName)
        {
            var provider = _modelRouter.GetProviderByModel(modelName);

            if (provider == null)
            {
                return new CommandParsedDTO
                {
                    Action = "error",
                    Entity = "",
                    Parameters = new Dictionary<string, object>
            {
                { "reason", $"Model '{modelName}' is not supported." }
            }
                };
            }

            try
            {
                // Prepend context to the prompt
                string fullPrompt = BuildPromptWithContext(prompt); // You can hardcode for now or make this dynamic later
                var requestBody = BuildRequestBody(fullPrompt, provider);

                var request = new HttpRequestMessage(HttpMethod.Post, provider.BaseUrl);

                if (provider.RequiresKey)
                {
                    if (string.IsNullOrWhiteSpace(provider.ApiKey))
                    {
                        return new CommandParsedDTO
                        {
                            Action = "error",
                            Entity = "",
                            Parameters = new Dictionary<string, object>
                    {
                        { "reason", $"API key not found for {provider.Name}" }
                    }
                        };
                    }

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

                var response = await _httpClient.SendAsync(request);

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    return new CommandParsedDTO
                    {
                        Action = "error",
                        Entity = "",
                        Parameters = new Dictionary<string, object>
                {
                    { "reason", $"Error {response.StatusCode}: {errorContent}" }
                }
                    };
                }

                var responseContent = await response.Content.ReadAsStringAsync();
                var parsedDto = ParseLLMResponse(responseContent, provider);

                return parsedDto;
            }
            catch (Exception ex)
            {
                return new CommandParsedDTO
                {
                    Action = "error",
                    Entity = "",
                    Parameters = new Dictionary<string, object>
            {
                { "reason", $"Exception: {ex.Message}" }
            }
                };
            }
        }


        private string BuildPromptWithContext(string userPrompt)
        {
            var context = @"
You are an AI assistant that converts natural language into structured JSON commands for Business Central data operations.
Your job is return only JSON NOT EXPLAINING NO FURTHER OR ADDED TEXT ONLY JSON UNDER THE FORMAT EXPLAINED BELOW
You can take actions: Create, Update, Delete, Get , Getall . 

Available Entities and Fields:

1. Customer:
- Customer_ID
- Full_Name
- Username
- Email
- Phone_Number
- Created_At

2. CopilotEntity:
- Entity_ID
- Customer_ID
- Title
- Description
- Status : this can ony accept Open , InProgress , Completed , Cancelled
- Created_At

You must return a JSON object with the following keys:
- ""Action"":

- ""Entity"": (Customer or CopilotEntity)
- ""Parameters"": key-value pairs matching the entity fields.
for the action youre giving basic create update get delete or getall 
//make sure to differenciate between get and getall please
Example:
{
  ""Action"": ""Create"",
  ""Entity"": ""Customer"",
  ""Parameters"": {
    ""Customer_ID"": ""55"" 
    ""Full_Name"": ""Jane Doe"",
    ""Email"": ""jane@example.com"",
    ""Phone_Number"": ""1234567890""
  }
}
**INSTRUCTION:
1-Customer_ID and Entity_ID SHOULD ALWAYS BE STRINGS NOT INTEGERS //""Customer_ID"": ""55"" 
2-you have to generate the paramaters that werent mentioned your goal is to parse through his prompt the max number of parammeters and return them all either parsed or generated
3-For Update and Delete actions, always include the primary key of the entity (e.g., Customer_ID for Customer).
4-Do not explain. Only return JSON.
";

            return $"{context}\nUser command: {userPrompt}";
        }


        private string BuildRequestBody(string fullPromptWithContext, LLMProviderConfig provider)
        {
            // All requests include a system message for consistent LLM behavior
            var messages = new[]
            {
        new { role = "system", content = "You are an AI assistant specialized in generating structured commands for Microsoft Dynamics 365 Business Central. Only return JSON." },
        new { role = "user", content = fullPromptWithContext }
    };

            object payload;

            switch (provider.Provider.ToLower())
            {
                case "openai":
                case "mistral":
                case "together":
                case "groq":
                    payload = new
                    {
                        model = provider.ModelName,
                        messages = messages,
                        temperature = 0.4,
                        max_tokens = 1000
                    };
                    break;

                case "anthropic":
                    payload = new
                    {
                        model = provider.ModelName,
                        messages = messages,
                        temperature = 0.4,
                        max_tokens = 1000,
                        system = "You are an AI assistant specialized in generating structured commands for Microsoft Dynamics 365 Business Central. Only return JSON."
                    };
                    break;

                default:
                    payload = new
                    {
                        prompt = fullPromptWithContext
                    };
                    break;
            }

            var json = JsonSerializer.Serialize(payload);
            Console.WriteLine($"[DEBUG] Request body for {provider.Provider}: {json}");
            return json;
        }

        private string CleanJson(string content)
        {
            if (content.StartsWith("```"))
            {
                int startIndex = content.IndexOf("{");
                int endIndex = content.LastIndexOf("}");

                if (startIndex >= 0 && endIndex > startIndex)
                {
                    return content.Substring(startIndex, endIndex - startIndex + 1);
                }
            }

            return content.Trim();
        }
        private CommandParsedDTO ParseLLMResponse(string responseContent, LLMProviderConfig provider)
        {
            string extractedJson = "";

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
                                extractedJson = content.GetString() ?? "";
                            }
                        }
                        break;

                    case "anthropic":
                        if (doc.RootElement.TryGetProperty("completion", out JsonElement completion))
                        {
                            extractedJson = completion.GetString() ?? "";
                        }
                        break;

                    default:
                        // fallback: assume full response *is* JSON
                        extractedJson = responseContent;
                        break;
                }


                if (string.IsNullOrWhiteSpace(extractedJson))
                {
                    Console.WriteLine("[ERROR] No content extracted from LLM response.");
                    return new CommandParsedDTO
                    {
                        Action = "error",
                        Entity = "unknown",
                        Parameters = new Dictionary<string, object>
                {
                    { "reason", "No content extracted from LLM response." },
                    { "rawResponse", responseContent }
                }
                    };
                }
                extractedJson = CleanJson(extractedJson);

                Console.WriteLine($"[DEBUG] Extracted JSON from LLM:\n{extractedJson}");

                var parsed = JsonSerializer.Deserialize<CommandParsedDTO>(extractedJson, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

                if (parsed == null || string.IsNullOrWhiteSpace(parsed.Action) || string.IsNullOrWhiteSpace(parsed.Entity))
                {
                    Console.WriteLine("[ERROR] Parsed command is missing Action or Entity.");
                    return new CommandParsedDTO
                    {
                        Action = "error",
                        Entity = "unknown",
                        Parameters = new Dictionary<string, object>
                {
                    { "reason", "Parsed result was missing required fields." },
                    { "rawJson", extractedJson }
                }
                    };
                }

                return parsed;
            }
            catch (JsonException jex)
            {
                Console.WriteLine($"[ERROR] Failed to parse LLM JSON: {jex.Message}");
                Console.WriteLine($"[DEBUG] Raw content:\n{extractedJson}");
                return new CommandParsedDTO
                {
                    Action = "error",
                    Entity = "unknown",
                    Parameters = new Dictionary<string, object>
            {
                { "reason", $"JsonException: {jex.Message}" },
                { "rawJson", extractedJson }
            }
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] Unexpected error while parsing LLM response: {ex.Message}");
                return new CommandParsedDTO
                {
                    Action = "error",
                    Entity = "unknown",
                    Parameters = new Dictionary<string, object>
            {
                { "reason", $"Unhandled exception: {ex.Message}" }
            }
                };
            }
        }

    }
}
