namespace XPilotCopilotAPI.DTOs
{
    public class PromptResponseDTO
    {
        public string? Response { get; set; }
        public string? ModelUsed { get; set; }
        public string? Status { get; set; }  //"Success" or "Error"
    }
}
