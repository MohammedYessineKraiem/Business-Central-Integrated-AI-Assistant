using System.Threading.Tasks;
using XPilotCopilotAPI.DTOs;

public interface ILlmService
{
    Task<CommandParsedDTO> ParseCommandAsync(string prompt, string model);
}
