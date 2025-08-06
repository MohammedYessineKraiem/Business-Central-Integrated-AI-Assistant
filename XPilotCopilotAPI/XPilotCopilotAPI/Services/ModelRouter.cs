using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Extensions.Options;
using Microsoft.Extensions.Configuration;
using XPilotCopilotAPI.Models;

namespace XPilotCopilotAPI.Services
{
    public class ModelRouter
    {
        private readonly List<LLMProviderConfig> _providers;

        public ModelRouter(IOptions<LLMSettings> options, IConfiguration configuration)
        {
            Console.WriteLine($"[DEBUG] Found {options.Value.LLMProviders.Count} providers in config");

            _providers = options.Value.LLMProviders
                .Select(p => {
                    var resolvedKey = p.RequiresKey
                        ? configuration[$"LLMApiKeys:{p.ApiKey}"] ?? ""
                        : "";

                    Console.WriteLine($"[DEBUG] Provider: {p.Name}, ApiKey template: {p.ApiKey}, Resolved key: {(!string.IsNullOrEmpty(resolvedKey) ? "Found" : "NOT FOUND")}");

                    return new LLMProviderConfig
                    {
                        Name = p.Name,
                        Provider = p.Provider,
                        Model = p.Model,
                        ModelName = p.ModelName,
                        BaseUrl = p.BaseUrl,
                        RequiresKey = p.RequiresKey,
                        ApiKey = resolvedKey
                    };
                })
                .ToList();
        }
            
        public LLMProviderConfig? GetProviderByModel(string modelName)
        {
            return _providers.FirstOrDefault(p => p.Model.Equals(modelName, StringComparison.OrdinalIgnoreCase));
        }
    }
}
