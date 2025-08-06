using System.Collections.Generic;

namespace XPilotCopilotAPI.Models
{
    public class LLMSettings
    {
        public List<LLMProviderConfig> LLMProviders { get; set; } = new List<LLMProviderConfig>();
    }
}
