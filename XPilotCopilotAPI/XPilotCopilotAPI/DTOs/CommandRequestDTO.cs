namespace XPilotCopilotAPI.DTOs
{
    public class CommandRequestDTO
    {
        public string Prompt { get; set; } = string.Empty;  // natural language command
        public string Model { get; set; } = string.Empty;   // e.g., "gpt-4", "local-llm"
    }
}
