using System.Threading.Tasks;
using XPilotCopilotAPI.DTOs;

public interface ICommandService
{
    Task<CommandResponseDTO> ExecuteCommandAsync(CommandParsedDTO command);
}
