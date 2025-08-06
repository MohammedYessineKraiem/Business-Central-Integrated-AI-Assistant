using XPilotCopilotAPI.DTOs;

namespace XPilotCopilotAPI.Services
{
    public interface IIntentParserService
    {
        Task<PromptClassificationResponseDTO> ClassifyPromptAsync(string prompt, string model);
    }
}
