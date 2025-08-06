using System.Collections.Generic;
using System.Threading.Tasks;
using XPilotCopilotAPI.DTOs;
using XPilotCopilotAPI.Models;

namespace XPilotCopilotAPI.DAOs
{
    public interface ICopilotEntityDao
    {
        Task<CommandResponseDTO> CreateAsync(CopilotEntity entity);
        Task<CommandResponseDTO> UpdateAsync(CopilotEntity entity);
        Task<CommandResponseDTO> DeleteAsync(string entityId);
        Task<CommandResponseDTO> GetAsync(string entityId);
        Task<CommandResponseDTO> GetAllAsync();
    }
}
