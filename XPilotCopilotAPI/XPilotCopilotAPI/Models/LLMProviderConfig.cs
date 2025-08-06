namespace XPilotCopilotAPI.Models
{
    public class LLMProviderConfig
    {
        public string Name { get; set; } = null!;
        public string Provider { get; set; } = null!;
        public string ModelName { get; set; } = null!;
        public string Model { get; set; } = null!;
        public string BaseUrl { get; set; } = null!;
        public string ApiKey { get; set; } = null!;
        public bool RequiresKey { get; set; }
    }


}
